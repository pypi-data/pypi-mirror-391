import json
import requests
import threading
import websocket
import logging
import enum
import datetime
import hashlib
import time
import urllib
import socket
import http.server
import socketserver
from urllib.parse import urlparse, parse_qs
from time import sleep
from datetime import datetime as dt

logger = logging.getLogger(__name__)

class position:
    prd:str
    exch:str
    instname:str
    symname:str
    exd:int
    optt:str
    strprc:float
    buyqty:int
    sellqty:int
    netqty:int
    def encode(self):
        return self.__dict__

class ProductType:
    Delivery = 'C'
    Intraday = 'I'
    Normal   = 'M'
    CF       = 'M'

class FeedType:
    TOUCHLINE = 1    
    SNAPQUOTE = 2
    
class PriceType:
    Market = 'MKT'
    Limit = 'LMT'
    StopLossLimit = 'SL-LMT'
    StopLossMarket = 'SL-MKT'

class BuyorSell:
    Buy = 'B'
    Sell = 'S'
    
def reportmsg(msg):
    #print(msg)
    logger.debug(msg)

def reporterror(msg):
    #print(msg)
    logger.error(msg)

def reportinfo(msg):
    #print(msg)
    logger.info(msg)

class NorenApi_oauth:
    __service_config = {
      'host': 'http://wsapihost/',
      'routes': {
          'authorize': '/QuickAuth',
          'logout': '/Logout',
          'forgot_password': '/ForgotPassword',
          'change_password': '/Changepwd',
          'watchlist_names': '/MWList',
          'watchlist': '/MarketWatch',
          'watchlist_add': '/AddMultiScripsToMW',
          'watchlist_delete': '/DeleteMultiMWScrips',
          'placeorder': '/PlaceOrder',
          'modifyorder': '/ModifyOrder',
          'cancelorder': '/CancelOrder',
          'exitorder': '/ExitSNOOrder',
          'product_conversion': '/ProductConversion',
          'orderbook': '/OrderBook',
          'tradebook': '/TradeBook',          
          'singleorderhistory': '/SingleOrdHist',
          'searchscrip': '/SearchScrip',
          'TPSeries' : '/TPSeries',     
          'optionchain' : '/GetOptionChain',     
          'holdings' : '/Holdings',
          'limits' : '/Limits',
          'positions': '/PositionBook',
          'scripinfo': '/GetSecurityInfo',
          'getquotes': '/GetQuotes',
          'span_calculator' :'/SpanCalc',
          'option_greek' :'/GetOptionGreek',
          'get_daily_price_series' :'/EODChartData',      
      },
      'websocket_endpoint': 'wss://wsendpoint/',
      #'eoddata_endpoint' : 'http://eodhost/'
    }

    def __init__(self, host, websocket):
        self.__service_config['host'] = host
        self.__service_config['websocket_endpoint'] = websocket
        #self.__service_config['eoddata_endpoint'] = eodhost

        # Create a requests session for connection pooling and reduced handshake overhead
        self.session = requests.Session()
        
        self.__websocket = None
        self.__websocket_connected = False
        self.__ws_mutex = threading.Lock()
        self.__on_error = None
        self.__on_disconnect = None
        self.__on_open = None
        self.__subscribe_callback = None
        self.__order_update_callback = None
        self.__subscribers = {}
        self.__market_status_messages = []
        self.__exchange_messages = []
    
    def _get_headers(self, additional_headers=None):
        """Get headers with Bearer token for API requests"""
        headers = {}
        if hasattr(self, '_NorenApi_oauth__susertoken') and self.__susertoken:
            headers['Authorization'] = f'Bearer {self.__susertoken}'
        if additional_headers:
            headers.update(additional_headers)
        return headers

    def __ws_run_forever(self):
        
        while self.__stop_event.is_set() == False:
            try:
                self.__websocket.run_forever( ping_interval=3,  ping_payload='{"t":"h"}')
            except Exception as e:
                logger.warning(f"websocket run forever ended in exception, {e}")
            
            sleep(0.1) # Sleep for 100ms between reconnection.

    def __ws_send(self, *args, **kwargs):
        while self.__websocket_connected == False:
            sleep(0.05)  # sleep for 50ms if websocket is not connected, wait for reconnection
        with self.__ws_mutex:
            ret = self.__websocket.send(*args, **kwargs)
        return ret

    def __on_close_callback(self, wsapp, close_status_code, close_msg):
        reportmsg(close_status_code)
        reportmsg(wsapp)

        self.__websocket_connected = False
        if self.__on_disconnect:
            self.__on_disconnect()

    def __on_open_callback(self, ws=None):
        self.__websocket_connected = True

        #prepare the data
        values              = { "t": "c" }
        values["uid"]       = self.__username        
        values["actid"]     = self.__username
        values["susertoken"]    = self.__susertoken
        values["source"]    = 'API'                

        payload = json.dumps(values)

        reportmsg(payload)
        self.__ws_send(payload)

        #self.__resubscribe()
        

    def __on_error_callback(self, ws=None, error=None):
        if(type(ws) is not websocket.WebSocketApp): # This workaround is to solve the websocket_client's compatiblity issue of older versions. ie.0.40.0 which is used in upstox. Now this will work in both 0.40.0 & newer version of websocket_client
            error = ws
        if self.__on_error:
            self.__on_error(error)

    def __on_data_callback(self, ws=None, message=None, data_type=None, continue_flag=None):
        #print(ws)
        #print(message)
        #print(data_type)
        #print(continue_flag)

        res = json.loads(message)

        if(self.__subscribe_callback is not None):
            if res['t'] == 'tk' or res['t'] == 'tf':
                self.__subscribe_callback(res)
                return
            if res['t'] == 'dk' or res['t'] == 'df':
                self.__subscribe_callback(res)
                return

        if(self.__on_error is not None):
            if res['t'] == 'ck' and res['s'] != 'OK':
                self.__on_error(res)
                return

        if(self.__order_update_callback is not None):
            if res['t'] == 'om':
                self.__order_update_callback(res)
                return

        if self.__on_open:
            if res['t'] == 'ck' and res['s'] == 'OK':
                self.__on_open()
                return


    def start_websocket(self, subscribe_callback = None, 
                        order_update_callback = None,
                        socket_open_callback = None,
                        socket_close_callback = None,
                        socket_error_callback = None):        
        """ Start a websocket connection for getting live data """
        self.__on_open = socket_open_callback
        self.__on_disconnect = socket_close_callback
        self.__on_error = socket_error_callback
        self.__subscribe_callback = subscribe_callback
        self.__order_update_callback = order_update_callback
        self.__stop_event = threading.Event()
        url = self.__service_config['websocket_endpoint'].format(access_token=self.__susertoken)
        reportmsg('connecting to {}'.format(url))

        self.__websocket = websocket.WebSocketApp(url,
                                                on_data=self.__on_data_callback,
                                                on_error=self.__on_error_callback,
                                                on_close=self.__on_close_callback,
                                                on_open=self.__on_open_callback)
        #th = threading.Thread(target=self.__send_heartbeat)
        #th.daemon = True
        #th.start()
        #if run_in_background is True:
        self.__ws_thread = threading.Thread(target=self.__ws_run_forever)
        self.__ws_thread.daemon = True
        self.__ws_thread.start()
        
    def close_websocket(self):
        if self.__websocket_connected == False:
            return
        self.__stop_event.set()        
        self.__websocket_connected = False
        self.__websocket.close()
        self.__ws_thread.join()

    def __get_access_token(self, client_id: str, secret_key: str, code: str):
        """Get access token using authorization code with optional proxy support"""
        url = f"https://go.mynt.in/NorenWClientAPI/GenAcsTok"
        checksum = hashlib.sha256(f"{client_id}{secret_key}{code}".encode()).hexdigest()

        payload = 'jData={\"code\":\"' + code + '\",\"checksum\":\"' + checksum + '\"}'
        headers = {
            'Content-Type': 'text/plain'
        }
        print(f"Access token URL: {url}")

        try:

            # Use session for connection pooling
            response = self.session.post(url, headers=headers, data=payload)
            print(f"Access token response: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                print(f"Access token data: {response_data}")
                return response_data
            else:
                print(f"Access token error: {response.text}")
                return None
        except Exception as e:
            print(f"Error getting access token: {e}")
            logging.error(f"Error getting access token: {e}")
            return None

    def Oauth_login_using_code(self, client_id, client_secret, code: str):
        """OAuth login using an existing authorization code
        
        This function allows you to login using an authorization code that you
        already have, without needing to set up a localhost callback server.
        
        Args:
            client_id (str): Your OAuth client ID
            client_secret (str): Your OAuth client secret
            code (str): The authorization code received from OAuth callback
            
        Returns:
            dict: Token response with susertoken on success, None on failure
        """
        if not code:
            print("\n" + "="*70)
            print("❌ INVALID AUTHORIZATION CODE")
            print("="*70)
            print("\n⚠️  Error: Authorization code cannot be empty.")
            print("   Please provide a valid authorization code.\n")
            return None
        
        print("\n" + "="*70)
        print("🔐 OAUTH LOGIN USING AUTHORIZATION CODE")
        print("="*70)
        print(f"\n🔄 Exchanging authorization code for access token...\n")
        
        # Exchange authorization code for access token
        token_response = self.__get_access_token(client_id, client_secret, code)
        
        if token_response and 'susertoken' in token_response:
            # Set up session
            self.__service_config["code"] = code
            self.__susertoken = token_response['susertoken']
            if 'uid' in token_response:
                self.__username = token_response['uid']
                self.__accountid = token_response['uid']
            
            # Update host URL after OAuth login
            self.__service_config['host'] = 'https://go.mynt.in/NorenWClientAPI/'
            
            print("\n" + "="*70)
            print("🎉 LOGIN SUCCESSFUL!")
            print("="*70)
            print(f"\n✅ Your session has been established successfully!")
            print(f"   • User ID: {self.__username}")
            print(f"   • Session Token: {self.__susertoken[:50]}...")
            print(f"   • API Endpoint: {self.__service_config['host']}")
            print("\n   You can now use the API to place orders, check positions, etc.\n")
            return token_response
        else:
            error_msg = "Unknown error occurred"
            if token_response and 'emsg' in token_response:
                error_msg = token_response['emsg']
            
            print("\n" + "="*70)
            print("❌ LOGIN FAILED")
            print("="*70)
            print(f"\n⚠️  Error: {error_msg}")
            print("\n   Please check:")
            print("   • Your client_id and client_secret are correct")
            print("   • The authorization code is valid and hasn't expired")
            print("   • The authorization code was generated for this client_id")
            print("   • Your IP address is whitelisted (if required)")
            print("   • Try generating a new authorization code\n")
            return None

    def Oauth_login(self, client_id, client_secret):
        """OAuth login flow with localhost callback server"""
        config = NorenApi_oauth.__service_config
        
        # Get public IP
        try:
            public_ip_response = self.session.get('https://api.ipify.org?format=json', timeout=5)
            public_ip = public_ip_response.json().get('ip', 'Unknown')
        except Exception as e:
            public_ip = "Unknown"
        
        # Create callback URL with localhost
        callback_port = 8189
        callback_url = f"http://localhost:{callback_port}/callback"
        
        # Generate OAuth authorization URL
        auth_url = f"https://go.mynt.in/OAuthlogin/authorize/oauth?client_id={client_id}"
        
        # Print clear, step-by-step instructions
        print("\n" + "="*70)
        print("OAuth LOGIN - STEP BY STEP INSTRUCTIONS")
        print("="*70)
        print("\n📋 INFORMATION:")
        print(f"   • Your Public IP: {public_ip}")
        print(f"   • Callback URL: {callback_url}")
        print(f"   (Note: Make sure this callback URL is registered in your OAuth app settings)")
        
        print("\n" + "-"*70)
        print("🔐 STEP 1: AUTHORIZE THE APPLICATION")
        print("-"*70)
        print(f"\n👉 Copy and open this URL in your web browser:\n")
        print(f"   {auth_url}\n")
        print("   After opening, you will be asked to login and authorize the application.")
        
        print("\n" + "-"*70)
        print("⏳ STEP 2: WAITING FOR AUTHORIZATION")
        print("-"*70)
        print("\n   The system is now waiting for you to complete the authorization...")
        print("   Once you authorize in the browser, you will be redirected back automatically.")
        print("   You can press Ctrl+C at any time to cancel.\n")
        
        # Variables to store the authorization code and result (using list for mutable reference)
        auth_code_container = [None]
        token_result_container = [None]  # Will store the token response
        error_message_container = [None]  # Will store error message
        callback_received = threading.Event()
        
        # Create a simple HTTP server to handle the callback
        class CallbackHandler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                parsed_path = urlparse(self.path)
                query_params = parse_qs(parsed_path.query)
                
                if 'code' in query_params:
                    auth_code_container[0] = query_params['code'][0]
                    callback_received.set()
                    
                    # Perform token exchange synchronously before responding
                    try:
                        token_response = self.server.token_exchange_func(
                            self.server.client_id, 
                            self.server.client_secret, 
                            auth_code_container[0]
                        )
                        token_result_container[0] = token_response
                        
                        if token_response and 'susertoken' in token_response:
                            # Success - Update host URL after OAuth login
                            self.server.service_config['host'] = 'https://go.mynt.in/NorenWClientAPI/'
                            
                            # Success
                            self.send_response(200)
                            self.send_header('Content-type', 'text/html')
                            self.end_headers()
                            html = b'<html><body><h1 style="color: green;">Authorization successful!</h1><p>You can close this window.</p></body></html>'
                            self.wfile.write(html)
                        else:
                            # Error - get error message
                            error_msg = "Unknown error occurred"
                            if token_response and 'emsg' in token_response:
                                error_msg = token_response['emsg']
                            error_message_container[0] = error_msg
                            
                            self.send_response(200)
                            self.send_header('Content-type', 'text/html')
                            self.end_headers()
                            # Escape HTML special characters
                            safe_error = error_msg.replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;')
                            html = f'<html><body><h1 style="color: red;">Authorization Failed</h1><p style="color: red; font-weight: bold;">Error: {safe_error}</p><p>Please check the console for more details.</p></body></html>'.encode('utf-8')
                            self.wfile.write(html)
                    except Exception as e:
                        error_msg = f"Exception during token exchange: {str(e)}"
                        error_message_container[0] = error_msg
                        self.send_response(200)
                        self.send_header('Content-type', 'text/html')
                        self.end_headers()
                        safe_error = error_msg.replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;')
                        html = f'<html><body><h1 style="color: red;">Authorization Failed</h1><p style="color: red; font-weight: bold;">Error: {safe_error}</p></body></html>'.encode('utf-8')
                        self.wfile.write(html)
                else:
                    self.send_response(400)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(b'<html><body><h1>Error: No authorization code received</h1></body></html>')
            
            def log_message(self, format, *args):
                # Suppress default logging
                pass
        
        # Start the callback server in a separate thread
        server = socketserver.TCPServer(("", callback_port), CallbackHandler)
        # Store token exchange function, credentials, and service config in server for callback handler to use
        server.token_exchange_func = self.__get_access_token
        server.client_id = client_id
        server.client_secret = client_secret
        server.service_config = self.__service_config  # Reference to service config for URL update
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        
        print("✅ Callback server is ready and waiting...\n")
        
        interrupted = False
        try:
            # Wait for callback with polling to allow KeyboardInterrupt
            timeout = 300  # 5 minutes total timeout
            poll_interval = 0.5  # Check every 0.5 seconds
            elapsed = 0
            
            while not callback_received.is_set() and elapsed < timeout:
                callback_received.wait(timeout=poll_interval)
                elapsed += poll_interval
                
        except KeyboardInterrupt:
            interrupted = True
            print("\n\n" + "="*70)
            print("🚫 LOGIN CANCELLED")
            print("="*70)
            print("\n⚠️  OAuth login process was cancelled by user (Ctrl+C)")
            print("\n   To try again, simply call Oauth_login() again.\n")
        finally:
            # Shutdown the server
            try:
                server.shutdown()
                server.server_close()
            except Exception as e:
                pass  # Ignore errors during shutdown
        
        if interrupted:
            return None
        
        auth_code = auth_code_container[0]
        if auth_code:
            print("\n" + "="*70)
            print("✅ AUTHORIZATION CODE RECEIVED")
            print("="*70)
            print("\n🔄 Processing authorization and generating access token...\n")
            
            # Token exchange is now done in the callback handler
            # Wait a moment for it to complete
            time.sleep(0.5)
            
            # Get the result from the callback handler
            token_response = token_result_container[0]
            
            if token_response and 'susertoken' in token_response:
                self.__susertoken = token_response['susertoken']
                if 'uid' in token_response:
                    self.__username = token_response['uid']
                    self.__accountid = token_response['uid']
                
                # Update host URL after OAuth login
                self.__service_config['host'] = 'https://go.mynt.in/NorenWClientAPI/'
                self.__service_config["code"] = auth_code
                print(f"Auth Code: {self.__service_config['code']}")
                
                print("\n" + "="*70)
                print("🎉 LOGIN SUCCESSFUL!")
                print("="*70)
                print(f"\n✅ Your session has been established successfully!")
                print(f"   • User ID: {self.__username}")
                print(f"   • Session Token: {self.__susertoken[:50]}...")
                print(f"   • API Endpoint: {self.__service_config['host']}")
                print("\n   You can now use the API to place orders, check positions, etc.\n")
                return token_response
            else:
                error_msg = error_message_container[0] or "Unknown error occurred"
                if token_response and 'emsg' in token_response:
                    error_msg = token_response['emsg']
                
                print("\n" + "="*70)
                print("❌ LOGIN FAILED")
                print("="*70)
                print(f"\n⚠️  Error: {error_msg}")
                print("\n   Please check:")
                print("   • Your client_id and client_secret are correct")
                print("   • The callback URL is properly registered in your OAuth app")
                print("   • Your IP address is whitelisted (if required)")
                print("   • Try the authorization process again\n")
                return None
        else:
            print("\n" + "="*70)
            print("⏱️  TIMEOUT")
            print("="*70)
            print("\n⚠️  No authorization code received within 5 minutes.")
            print("\n   This could happen if:")
            print("   • You didn't complete the authorization in the browser")
            print("   • The browser was closed before completing authorization")
            print("   • There was a network issue")
            print("\n   Please try again by calling Oauth_login() again.\n")
            return None


    def set_session(self, userid, password, usertoken):
        
        self.__username   = userid
        self.__accountid  = userid
        self.__password   = password
        self.__susertoken = usertoken

        reportmsg(f'{userid} session set to : {self.__susertoken}')

        return True

    def forgot_password(self, userid, pan, dob):
        config = NorenApi_oauth.__service_config

        #prepare the uri
        url = f"{config['host']}{config['routes']['forgot_password']}" 
        reportmsg(url)

        #prepare the data
        values              = { "source": "API" }
        values["uid"]       = userid
        values["pan"]       = pan
        values["dob"]       = dob

        payload = 'jData=' + json.dumps(values)
        reportmsg("Req:" + payload)

        res = self.session.post(url, data=payload, headers=self._get_headers())
        reportmsg("Reply:" + res.text)

        resDict = json.loads(res.text)
        
        if resDict['stat'] != 'Ok':            
            return None
        
        return resDict

    def logout(self):
        config = NorenApi_oauth.__service_config

        #prepare the uri
        url = f"{config['host']}{config['routes']['logout']}" 
        reportmsg(url)
        #prepare the data
        values              = {'ordersource':'API'}
        values["uid"]       = self.__username
        
        payload = 'jData=' + json.dumps(values)
        
        reportmsg(payload)

        res = self.session.post(url, data=payload, headers=self._get_headers())
        reportmsg(res.text)

        resDict = json.loads(res.text)
        if resDict['stat'] != 'Ok':            
            return None

        self.__username   = None
        self.__accountid  = None
        self.__password   = None
        self.__susertoken = None

        return resDict

    def subscribe(self, instrument, feed_type=FeedType.TOUCHLINE):
        values = {}

        if(feed_type == FeedType.TOUCHLINE):
            values['t'] =  't'
        elif(feed_type == FeedType.SNAPQUOTE):
            values['t'] =  'd'
        else:
            values['t'] =  str(feed_type)

        if type(instrument) == list:
            values['k'] = '#'.join(instrument)
        else :
            values['k'] = instrument

        data = json.dumps(values)

        #print(data)
        self.__ws_send(data)

    def unsubscribe(self, instrument, feed_type=FeedType.TOUCHLINE):
        values = {}

        if(feed_type == FeedType.TOUCHLINE):
            values['t'] =  'u'
        elif(feed_type == FeedType.SNAPQUOTE):
            values['t'] =  'ud'
        
        if type(instrument) == list:
            values['k'] = '#'.join(instrument)
        else :
            values['k'] = instrument

        data = json.dumps(values)

        #print(data)
        self.__ws_send(data)

    def subscribe_orders(self):
        values = {'t': 'o'}
        values['actid'] = self.__accountid        

        data = json.dumps(values)

        reportmsg(data)
        self.__ws_send(data)

    def get_watch_list_names(self):
        config = NorenApi_oauth.__service_config

        #prepare the uri
        url = f"{config['host']}{config['routes']['watchlist_names']}" 
        reportmsg(url)
        #prepare the data
        values              = {'ordersource':'API'}
        values["uid"]       = self.__username
        
        payload = 'jData=' + json.dumps(values)
        
        reportmsg(payload)

        res = self.session.post(url, data=payload, headers=self._get_headers())
        reportmsg(res.text)

        resDict = json.loads(res.text)
        if resDict['stat'] != 'Ok':            
            return None

        return resDict

    def get_watch_list(self, wlname):
        config = NorenApi_oauth.__service_config

        #prepare the uri
        url = f"{config['host']}{config['routes']['watchlist']}" 
        reportmsg(url)
        #prepare the data
        values              = {'ordersource':'API'}
        values["uid"]       = self.__username
        values["wlname"]    = wlname
        
        payload = 'jData=' + json.dumps(values)
        
        reportmsg(payload)

        res = self.session.post(url, data=payload, headers=self._get_headers())
        reportmsg(res.text)

        resDict = json.loads(res.text)
        if resDict['stat'] != 'Ok':            
            return None

        return resDict


    def add_watch_list_scrip(self, wlname, instrument):
        config = NorenApi_oauth.__service_config

        #prepare the uri
        url = f"{config['host']}{config['routes']['watchlist_add']}" 
        reportmsg(url)
        #prepare the data
        values              = {'ordersource':'API'}
        values["uid"]       = self.__username
        values["wlname"]    = wlname

        if type(instrument) == list:
            values['scrips'] = '#'.join(instrument)
        else :
            values['scrips'] = instrument
        payload = 'jData=' + json.dumps(values)
        
        reportmsg(payload)

        res = self.session.post(url, data=payload, headers=self._get_headers())
        reportmsg(res.text)

        resDict = json.loads(res.text)
        if resDict['stat'] != 'Ok':            
            return None

        return resDict

    def delete_watch_list_scrip(self, wlname, instrument):
        config = NorenApi_oauth.__service_config

        #prepare the uri
        url = f"{config['host']}{config['routes']['watchlist_delete']}" 
        reportmsg(url)
        #prepare the data
        values              = {'ordersource':'API'}
        values["uid"]       = self.__username
        values["wlname"]    = wlname

        if type(instrument) == list:
            values['scrips'] = '#'.join(instrument)
        else :
            values['scrips'] = instrument
        payload = 'jData=' + json.dumps(values)
        
        reportmsg(payload)

        res = self.session.post(url, data=payload, headers=self._get_headers())
        reportmsg(res.text)

        resDict = json.loads(res.text)
        if resDict['stat'] != 'Ok':            
            return None

        return resDict


    def place_order(self, buy_or_sell, product_type,
                    exchange, tradingsymbol, quantity, discloseqty,
                    price_type, price=0.0, trigger_price=0.0,
                    retention='DAY', amo='NO', remarks=None, bookloss_price = 0.0, bookprofit_price = 0.0, trail_price = 0.0):
        config = NorenApi_oauth.__service_config

        #prepare the uri
        url = f"{config['host']}{config['routes']['placeorder']}" 
        reportmsg(url)
        #prepare the data
        values              = {'ordersource':'API'}
        values["uid"]       = self.__username
        values["actid"]     = self.__accountid
        values["trantype"]  = buy_or_sell
        values["prd"]       = product_type
        values["exch"]      = exchange
        values["tsym"]      = urllib.parse.quote_plus(tradingsymbol)
        values["qty"]       = str(quantity)
        values["dscqty"]    = str(discloseqty)        
        values["prctyp"]    = price_type
        values["prc"]       = str(price)
        values["trgprc"]    = str(trigger_price)
        values["ret"]       = retention
        values["remarks"]   = remarks
        values["amo"]       = amo
        if values["amo"]=="NO":
            del values['amo']
        #if cover order or high leverage order
        if product_type == 'H':            
            values["blprc"]       = str(bookloss_price)
            #trailing price
            if trail_price != 0.0:
                values["trailprc"] = str(trail_price)

        #bracket order
        if product_type == 'B':            
            values["blprc"]       = str(bookloss_price)
            values["bpprc"]       = str(bookprofit_price)
            #trailing price
            if trail_price != 0.0:
                values["trailprc"] = str(trail_price)

        payload = 'jData=' + json.dumps(values)
        
        reportmsg(payload)

        res = self.session.post(url, data=payload, headers=self._get_headers())
        reportmsg(res.text)

        resDict = json.loads(res.text)
        if resDict['stat'] != 'Ok':            
            return None

        return resDict

    def modify_order(self, orderno, exchange, tradingsymbol, newquantity,
                    newprice_type, newprice=0.0, newtrigger_price=None, bookloss_price = 0.0, bookprofit_price = 0.0, trail_price = 0.0):
        config = NorenApi_oauth.__service_config

        #prepare the uri
        url = f"{config['host']}{config['routes']['modifyorder']}" 
        print(url)

        #prepare the data
        values                  = {'ordersource':'API'}
        values["uid"]           = self.__username
        values["actid"]         = self.__accountid
        values["norenordno"]    = str(orderno)
        values["exch"]          = exchange
        values["tsym"]          = urllib.parse.quote_plus(tradingsymbol)
        values["qty"]           = str(newquantity)
        values["prctyp"]        = newprice_type        
        values["prc"]           = str(newprice)

        if (newprice_type == 'SL-LMT') or (newprice_type == 'SL-MKT'):
            if (newtrigger_price != None):
                values["trgprc"] = str(newtrigger_price)
            else:
                reporterror('trigger price is missing')
                return None

        #if cover order or high leverage order
        if bookloss_price != 0.0:            
            values["blprc"]       = str(bookloss_price)
        #trailing price
        if trail_price != 0.0:
            values["trailprc"] = str(trail_price)         
        #book profit of bracket order   
        if bookprofit_price != 0.0:
            values["bpprc"]       = str(bookprofit_price)
        
        payload = 'jData=' + json.dumps(values)
        
        reportmsg(payload)

        res = self.session.post(url, data=payload, headers=self._get_headers())
        reportmsg(res.text)

        resDict = json.loads(res.text)
        if resDict['stat'] != 'Ok':            
            return None

        return resDict

    def cancel_order(self, orderno):
        config = NorenApi_oauth.__service_config

        #prepare the uri
        url = f"{config['host']}{config['routes']['cancelorder']}" 
        print(url)

        #prepare the data
        values              = {'ordersource':'API'}
        values["uid"]       = self.__username
        values["norenordno"]    = str(orderno)
        
        payload = 'jData=' + json.dumps(values)
        
        reportmsg(payload)

        res = self.session.post(url, data=payload, headers=self._get_headers())
        print(res.text)

        resDict = json.loads(res.text)
        if resDict['stat'] != 'Ok':            
            return None

        return resDict

    def exit_order(self, orderno, product_type):
        config = NorenApi_oauth.__service_config

        #prepare the uri
        url = f"{config['host']}{config['routes']['exitorder']}" 
        print(url)

        #prepare the data
        values              = {'ordersource':'API'}
        values["uid"]       = self.__username
        values["norenordno"]    = orderno
        values["prd"]           = product_type
        
        payload = 'jData=' + json.dumps(values)
        
        reportmsg(payload)

        res = self.session.post(url, data=payload, headers=self._get_headers())
        reportmsg(res.text)

        resDict = json.loads(res.text)
        if resDict['stat'] != 'Ok':            
            return None

        return resDict

    def position_product_conversion(self, exchange, tradingsymbol, quantity, new_product_type, previous_product_type, buy_or_sell, day_or_cf):
        '''
        Coverts a day or carryforward position from one product to another. 
        '''
        config = NorenApi_oauth.__service_config

        #prepare the uri
        url = f"{config['host']}{config['routes']['product_conversion']}" 
        print(url)

        #prepare the data
        values              = {'ordersource':'API'}
        values["uid"]       = self.__username
        values["actid"]     = self.__accountid        
        values["exch"]      = exchange
        values["tsym"]      = urllib.parse.quote_plus(tradingsymbol)
        values["qty"]       = str(quantity)
        values["prd"]       = new_product_type
        values["prevprd"]   = previous_product_type
        values["trantype"]  = buy_or_sell
        values["postype"]   = day_or_cf
        
        payload = 'jData=' + json.dumps(values)
        
        reportmsg(payload)

        res = self.session.post(url, data=payload, headers=self._get_headers())
        reportmsg(res.text)

        resDict = json.loads(res.text)
        
        if resDict['stat'] != 'Ok':            
            return None

        return resDict


    def single_order_history(self, orderno):
        config = NorenApi_oauth.__service_config

        #prepare the uri
        url = f"{config['host']}{config['routes']['singleorderhistory']}" 
        print(url)
        
        #prepare the data
        values              = {'ordersource':'API'}
        values["uid"]       = self.__username
        values["norenordno"]    = orderno
        
        payload = 'jData=' + json.dumps(values)
        
        reportmsg(payload)

        res = self.session.post(url, data=payload, headers=self._get_headers())
        reportmsg(res.text)

        resDict = json.loads(res.text)
        #error is a json with stat and msg wchih we printed earlier.
        if type(resDict) != list:                            
                return None

        return resDict


    def get_order_book(self):
        config = NorenApi_oauth.__service_config

        #prepare the uri
        url = f"{config['host']}{config['routes']['orderbook']}" 
        reportmsg(url)

        #prepare the data
        values              = {'ordersource':'API'}
        values["uid"]       = self.__username
        
        payload = 'jData=' + json.dumps(values)
        
        reportmsg(payload)

        res = self.session.post(url, data=payload, headers=self._get_headers())
        reportmsg(res.text)

        resDict = json.loads(res.text)
        
        #error is a json with stat and msg wchih we printed earlier.
        if type(resDict) != list:                            
                return None

        return resDict

    def get_trade_book(self):
        config = NorenApi_oauth.__service_config

        #prepare the uri
        url = f"{config['host']}{config['routes']['tradebook']}" 
        reportmsg(url)

        #prepare the data
        values              = {'ordersource':'API'}
        values["uid"]       = self.__username
        values["actid"]     = self.__accountid
        
        payload = 'jData=' + json.dumps(values)
        
        reportmsg(payload)

        res = self.session.post(url, data=payload, headers=self._get_headers())
        reportmsg(res.text)

        resDict = json.loads(res.text)
        
        #error is a json with stat and msg wchih we printed earlier.
        if type(resDict) != list:                            
                return None

        return resDict

    def searchscrip(self, exchange, searchtext):
        config = NorenApi_oauth.__service_config

        #prepare the uri
        url = f"{config['host']}{config['routes']['searchscrip']}" 
        reportmsg(url)
        
        if searchtext == None:
            reporterror('search text cannot be null')
            return None
        
        values              = {}
        values["uid"]       = self.__username
        values["exch"]      = exchange
        values["stext"]     = urllib.parse.quote_plus(searchtext)       
        
        payload = 'jData=' + json.dumps(values)
        
        reportmsg(payload)

        res = self.session.post(url, data=payload, headers=self._get_headers())
        reportmsg(res.text)

        resDict = json.loads(res.text)

        if resDict['stat'] != 'Ok':            
            return None        

        return resDict

    def get_option_chain(self, exchange, tradingsymbol, strikeprice, count=2):
        config = NorenApi_oauth.__service_config

        #prepare the uri
        url = f"{config['host']}{config['routes']['optionchain']}" 
        reportmsg(url)
        
        
        values              = {}
        values["uid"]       = self.__username
        values["exch"]      = exchange
        values["tsym"]      = urllib.parse.quote_plus(tradingsymbol)       
        values["strprc"]    = str(strikeprice)
        values["cnt"]       = str(count)       
        
        
        payload = 'jData=' + json.dumps(values)
        
        reportmsg(payload)

        res = self.session.post(url, data=payload, headers=self._get_headers())
        reportmsg(res.text)

        resDict = json.loads(res.text)

        if resDict['stat'] != 'Ok':            
            return None        

        return resDict

    def get_security_info(self, exchange, token):
        config = NorenApi_oauth.__service_config

        #prepare the uri
        url = f"{config['host']}{config['routes']['scripinfo']}" 
        reportmsg(url)        
        
        values              = {}
        values["uid"]       = self.__username
        values["exch"]      = exchange
        values["token"]     = token       
        
        payload = 'jData=' + json.dumps(values)
        
        reportmsg(payload)

        res = self.session.post(url, data=payload, headers=self._get_headers())
        reportmsg(res.text)

        resDict = json.loads(res.text)

        if resDict['stat'] != 'Ok':            
            return None        

        return resDict

    def get_quotes(self, exchange, token):
        config = NorenApi_oauth.__service_config

        #prepare the uri
        url = f"{config['host']}{config['routes']['getquotes']}" 
        reportmsg(url)        
        
        values              = {}
        values["uid"]       = self.__username
        values["exch"]      = exchange
        values["token"]     = token       
        
        payload = 'jData=' + json.dumps(values)
        
        reportmsg(payload)

        res = self.session.post(url, data=payload, headers=self._get_headers())
        reportmsg(res.text)

        resDict = json.loads(res.text)

        if resDict['stat'] != 'Ok':     
            return None        

        return resDict

    def get_time_price_series(self, exchange, token, starttime=None, endtime=None, interval= None):
        '''
        gets the chart data 
        interval possible values 1, 3, 5 , 10, 15, 30, 60, 120, 240
        '''
        config = NorenApi_oauth.__service_config

        #prepare the uri
        url = f"{config['host']}{config['routes']['TPSeries']}" 
        reportmsg(url)

        #prepare the data
        if starttime == None:
            timestring = time.strftime('%d-%m-%Y') + ' 00:00:00'
            timeobj = time.strptime(timestring,'%d-%m-%Y %H:%M:%S')
            starttime = time.mktime(timeobj)

        #
        values              = {'ordersource':'API'}
        values["uid"]       = self.__username
        values["exch"]      = exchange
        values["token"]     = token
        values["st"] = str(starttime)
        if endtime != None:
            values["et"]   = str(endtime)
        if interval != None:
            values["intrv"] = str(interval)

        payload = 'jData=' + json.dumps(values)
        
        reportmsg(payload)

        res = self.session.post(url, data=payload, headers=self._get_headers())
        reportmsg(res.text)

        resDict = json.loads(res.text)
        
        #error is a json with stat and msg wchih we printed earlier.
        if type(resDict) != list:                            
                return None

        return resDict

    def get_daily_price_series(self, exchange, tradingsymbol, startdate=None, enddate=None):
        config = NorenApi_oauth.__service_config

        #prepare the uri
        #url = f"{config['eoddata_endpoint']}" 
        url = f"{config['host']}{config['routes']['get_daily_price_series']}" 
        reportmsg(url)

        #prepare the data
        if startdate == None:  
            week_ago = datetime.date.today() - datetime.timedelta(days=7)
            startdate = dt.combine(week_ago, dt.min.time()).timestamp()

        if enddate == None:            
            enddate = dt.now().timestamp()

        #
        values              = {}
        values["uid"]       = self.__username
        values["sym"]      = '{0}:{1}'.format(exchange, tradingsymbol)
        values["from"]     = str(startdate)
        values["to"]       = str(enddate)
        
        payload = 'jData=' + json.dumps(values)
        #payload = json.dumps(values)
        reportmsg(payload)

        headers = self._get_headers({"Content-Type": "application/json; charset=utf-8"})
        res = self.session.post(url, data=payload, headers=headers)
        reportmsg(res)

        if res.status_code != 200:
            return None

        if len(res.text) == 0:
            return None

        resDict = json.loads(res.text)
        
        #error is a json with stat and msg wchih we printed earlier.
        if type(resDict) != list:                            
            return None

        return resDict
        
    def get_holdings(self, product_type = None):
        config = NorenApi_oauth.__service_config

        #prepare the uri
        url = f"{config['host']}{config['routes']['holdings']}" 
        reportmsg(url)
        
        if product_type == None:
            product_type = ProductType.Delivery
        
        values              = {}
        values["uid"]       = self.__username
        values["actid"]     = self.__accountid
        values["prd"]       = product_type       
        
        payload = 'jData=' + json.dumps(values)
        
        reportmsg(payload)

        res = self.session.post(url, data=payload, headers=self._get_headers())
        reportmsg(res.text)

        resDict = json.loads(res.text)

        if type(resDict) != list:                            
                return None

        return resDict

    def get_limits(self, product_type = None, segment = None, exchange = None):
        config = NorenApi_oauth.__service_config

        #prepare the uri
        url = f"{config['host']}{config['routes']['limits']}" 
        reportmsg(url)        
        
        values              = {}
        values["uid"]       = self.__username
        values["actid"]     = self.__accountid
        
        if product_type != None:
            values["prd"]       = product_type       
        
        if product_type != None:
            values["seg"]       = segment       
        
        if exchange != None:
            values["exch"]       = exchange       
        
        payload = 'jData=' + json.dumps(values)
        
        reportmsg(payload)

        res = self.session.post(url, data=payload, headers=self._get_headers())
        reportmsg(res.text)

        resDict = json.loads(res.text)        

        return resDict

    def get_positions(self):
        config = NorenApi_oauth.__service_config

        #prepare the uri
        url = f"{config['host']}{config['routes']['positions']}" 
        reportmsg(url)        
        
        values              = {}
        values["uid"]       = self.__username
        values["actid"]     = self.__accountid
        
        payload = 'jData=' + json.dumps(values)
        
        reportmsg(payload)

        res = self.session.post(url, data=payload, headers=self._get_headers())
        reportmsg(res.text)

        resDict = json.loads(res.text)

        if type(resDict) != list:                            
            return None

        return resDict

    def span_calculator(self,actid,positions:list):
        config = NorenApi_oauth.__service_config
        #prepare the uri
        url = f"{config['host']}{config['routes']['span_calculator']}" 
        reportmsg(url) 

        senddata = {}
        senddata['actid'] =self.__accountid 
        senddata['pos'] = positions
        payload = 'jData=' + json.dumps(senddata,default=lambda o: o.encode())
        reportmsg(payload)

        res = self.session.post(url, data=payload, headers=self._get_headers())
        reportmsg(res.text)

        resDict = json.loads(res.text)        

        return resDict
        
    def option_greek(self,expiredate,StrikePrice,SpotPrice,InterestRate,Volatility,OptionType):
        config = NorenApi_oauth.__service_config 

        #prepare the uri
        url = f"{config['host']}{config['routes']['option_greek']}" 
        reportmsg(url)

        #prepare the data
        values               = { "source": "API" }
        values["actid"]     = self.__accountid
        values["exd"]        = expiredate
        values["strprc"]     = StrikePrice 
        values["sptprc"]     = SpotPrice
        values["int_rate"]   = InterestRate	
        values["volatility"] = Volatility
        values["optt"]       = OptionType

        payload = 'jData=' + json.dumps(values)
        
        reportmsg(payload)

        res = self.session.post(url, data=payload, headers=self._get_headers())
        reportmsg(res.text)

        resDict = json.loads(res.text)        

        return resDict
