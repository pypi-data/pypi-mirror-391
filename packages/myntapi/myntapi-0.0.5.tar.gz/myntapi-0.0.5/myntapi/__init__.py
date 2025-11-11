from myntapi.noren import  NorenApi
from myntapi.noren_oauth import  NorenApi_oauth
from threading import Timer
import pandas as pd
import time
import concurrent.futures

api = None

class Order:
    def __init__(self, buy_or_sell:str = None, product_type:str = None,
                    exchange: str = None, tradingsymbol:str =None, 
                    price_type: str = None, quantity: int = None, 
                    price: float = None,trigger_price:float = None, discloseqty: int = 0,
                    retention:str = 'DAY', remarks: str = "tag",
                    order_id:str = None):
        self.buy_or_sell=buy_or_sell
        self.product_type=product_type
        self.exchange=exchange
        self.tradingsymbol=tradingsymbol
        self.quantity=quantity
        self.discloseqty=discloseqty
        self.price_type=price_type
        self.price=price
        self.trigger_price=trigger_price
        self.retention=retention
        self.remarks=remarks
        self.order_id=None


    #print(ret)

    


def get_time(time_string):
    data = time.strptime(time_string,'%d-%m-%Y %H:%M:%S')

    return time.mktime(data)


class app(NorenApi):
    def __init__(self):
        NorenApi.__init__(self, host='https://go.mynt.in/NorenWClientTP/', websocket='wss://go.mynt.in/NorenWSTP/')        
        global api
        api = self
        self.remarks='Python library'

    # def place_basket(self, orders):

    #     resp_err = 0
    #     resp_ok  = 0
    #     result   = []
    #     with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:

    #         future_to_url = {executor.submit(self.place_order, order): order for order in  orders}
    #         for future in concurrent.futures.as_completed(future_to_url):
    #             url = future_to_url[future]
    #         try:
    #             result.append(future.result())
    #         except Exception as exc:
    #             print(exc)
    #             resp_err = resp_err + 1
    #         else:
    #             resp_ok = resp_ok + 1

    #     return result
                
    def placeOrder(self,order):
        ret = NorenApi.place_order(self, buy_or_sell=order["buy_or_sell"], product_type=order["product_type"],exchange=order["exchange"], tradingsymbol=order["tradingsymbol"], 
                            quantity=order["quantity"], discloseqty=order["discloseqty"], price_type=order["price_type"], 
                            price=order["price"], trigger_price=order.get("trigger_price"),
                            retention=order.get("retention") if "retention" in order else 'DAY', remarks=self.remarks)
        print(ret)

        return ret

    def place_basket(self, orders):
        print(orders)
        resp_err = 0
        resp_ok  = 0
        result   = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:

            future_to_url = {executor.submit(self.placeOrder,order): order for order in  orders}
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    resp=future.result()
                    url.update(resp)
                    result.append(url)
                except Exception as exc:
                    print(exc)
                    resp_err = resp_err + 1
                else:
                    resp_ok = resp_ok + 1

        return result


    def close_all_position(self,_type_=None):
        ret=self.get_positions()

        # ret=[{'stat': 'Ok', 'uid': 'ZP00435', 'actid': 'ZP00435', 'exch': 'NSE', 'tsym': 'IDEA-EQ', 's_prdt_ali': 'MIS', 'prd': 'I', 'token': '14366', 'instname': 'EQ', 'frzqty': '6133640', 'pp': '2', 'ls': '1', 'ti': '0.05', 'mult': '1', 'prcftr': '1.000000', 'daybuyqty': '1', 'daysellqty': '0', 'daybuyamt': '16.30', 'daybuyavgprc': '16.30', 'daysellamt': '0.00', 'daysellavgprc': '0.00', 'cfbuyqty': '0', 'cfsellqty': '0', 'cfbuyamt': '0.00', 'cfbuyavgprc': '0.00', 'cfsellamt': '0.00', 'cfsellavgprc': '0.00', 'openbuyqty': '0', 'opensellqty': '0', 'openbuyamt': '0.00', 'openbuyavgprc': '0.00', 'opensellamt': '0.00', 'opensellavgprc': '0.00', 'dayavgprc': '16.30', 'netqty': '1', 'netavgprc': '16.30', 'upldprc': '0.00', 'netupldprc': '16.30', 'lp': '16.15', 'urmtom': '-0.15', 'bep': '16.30', 'totbuyamt': '16.30', 'totsellamt': '0.00', 'totbuyavgprc': '16.30', 'totsellavgprc': '0.00', 'rpnl': '-0.00'}]

        place_order_data=[]
        resp_err_data=[]
        for orders in ret:
            if ("positive" if int(orders.get('netqty', 0)) > 0 else ("negative" if int(orders.get('netqty', 0)) < 0 else 0))!=0:
                if _type_ is None:
                    place_order_data.append({
                        "buy_or_sell":"S" if int(orders.get('netqty', 0)) > 0 else "B" ,
                        "product_type": orders.get("prd"),
                        "exchange":orders.get("exch"), 
                        "tradingsymbol":orders.get("tsym"), 
                        "quantity":orders.get("netqty"), 
                        "discloseqty":"0", 
                        "price_type":"MKT",
                        "price":"0"
                    })
                else:
                    for condition in _type_:
                        if condition["tradingsymbol"]==orders.get("tsym") and condition["order_type"]==orders.get("s_prdt_ali"):
                            if int(orders.get("netqty"))-int(condition["quantity"])>=0:
                                place_order_data.append({
                                    "buy_or_sell":"S" if int(orders.get('netqty', 0)) > 0 else "B" ,
                                    "product_type": orders.get("prd"),
                                    "exchange":orders.get("exch"), 
                                    "tradingsymbol":orders.get("tsym"), 
                                    "quantity":orders.get("netqty"), 
                                    "discloseqty":"0", 
                                    "price_type":"MKT",
                                    "price":"0"
                                })
                            else:
                                resp_err_data.append({"error":"quantity is greater than position","tradingsymbol":condition["tradingsymbol"],"order_type":condition["order_type"]})
        order_resp=self.place_basket(orders=place_order_data)
        order_resp=order_resp+resp_err_data
        return order_resp


class app_oauth(NorenApi_oauth):
    def __init__(self):
        NorenApi_oauth.__init__(self, host='https://go.mynt.in/NorenWClientAPI/', websocket='wss://go.mynt.in/NorenWSAPI/')        
        global api
        api = self
        self.remarks='Python library'
        
    def Oauth_login(self, client_id, client_secret):
        return NorenApi_oauth.Oauth_login(self, client_id, client_secret)

    # def place_basket(self, orders):

    #     resp_err = 0
    #     resp_ok  = 0
    #     result   = []
    #     with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:

    #         future_to_url = {executor.submit(self.place_order, order): order for order in  orders}
    #         for future in concurrent.futures.as_completed(future_to_url):
    #             url = future_to_url[future]
    #         try:
    #             result.append(future.result())
    #         except Exception as exc:
    #             print(exc)
    #             resp_err = resp_err + 1
    #         else:
    #             resp_ok = resp_ok + 1

    #     return result
                
    def placeOrder(self,order):
        ret = NorenApi.place_order(self, buy_or_sell=order["buy_or_sell"], product_type=order["product_type"],exchange=order["exchange"], tradingsymbol=order["tradingsymbol"], 
                            quantity=order["quantity"], discloseqty=order["discloseqty"], price_type=order["price_type"], 
                            price=order["price"], trigger_price=order.get("trigger_price"),
                            retention=order.get("retention") if "retention" in order else 'DAY', remarks=self.remarks)
        print(ret)

        return ret

    def place_basket(self, orders):
        print(orders)
        resp_err = 0
        resp_ok  = 0
        result   = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:

            future_to_url = {executor.submit(self.placeOrder,order): order for order in  orders}
            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    resp=future.result()
                    url.update(resp)
                    result.append(url)
                except Exception as exc:
                    print(exc)
                    resp_err = resp_err + 1
                else:
                    resp_ok = resp_ok + 1

        return result


    def close_all_position(self,_type_=None):
        ret=self.get_positions()

        # ret=[{'stat': 'Ok', 'uid': 'ZP00435', 'actid': 'ZP00435', 'exch': 'NSE', 'tsym': 'IDEA-EQ', 's_prdt_ali': 'MIS', 'prd': 'I', 'token': '14366', 'instname': 'EQ', 'frzqty': '6133640', 'pp': '2', 'ls': '1', 'ti': '0.05', 'mult': '1', 'prcftr': '1.000000', 'daybuyqty': '1', 'daysellqty': '0', 'daybuyamt': '16.30', 'daybuyavgprc': '16.30', 'daysellamt': '0.00', 'daysellavgprc': '0.00', 'cfbuyqty': '0', 'cfsellqty': '0', 'cfbuyamt': '0.00', 'cfbuyavgprc': '0.00', 'cfsellamt': '0.00', 'cfsellavgprc': '0.00', 'openbuyqty': '0', 'opensellqty': '0', 'openbuyamt': '0.00', 'openbuyavgprc': '0.00', 'opensellamt': '0.00', 'opensellavgprc': '0.00', 'dayavgprc': '16.30', 'netqty': '1', 'netavgprc': '16.30', 'upldprc': '0.00', 'netupldprc': '16.30', 'lp': '16.15', 'urmtom': '-0.15', 'bep': '16.30', 'totbuyamt': '16.30', 'totsellamt': '0.00', 'totbuyavgprc': '16.30', 'totsellavgprc': '0.00', 'rpnl': '-0.00'}]

        place_order_data=[]
        resp_err_data=[]
        for orders in ret:
            if ("positive" if int(orders.get('netqty', 0)) > 0 else ("negative" if int(orders.get('netqty', 0)) < 0 else 0))!=0:
                if _type_ is None:
                    place_order_data.append({
                        "buy_or_sell":"S" if int(orders.get('netqty', 0)) > 0 else "B" ,
                        "product_type": orders.get("prd"),
                        "exchange":orders.get("exch"), 
                        "tradingsymbol":orders.get("tsym"), 
                        "quantity":orders.get("netqty"), 
                        "discloseqty":"0", 
                        "price_type":"MKT",
                        "price":"0"
                    })
                else:
                    for condition in _type_:
                        if condition["tradingsymbol"]==orders.get("tsym") and condition["order_type"]==orders.get("s_prdt_ali"):
                            if int(orders.get("netqty"))-int(condition["quantity"])>=0:
                                place_order_data.append({
                                    "buy_or_sell":"S" if int(orders.get('netqty', 0)) > 0 else "B" ,
                                    "product_type": orders.get("prd"),
                                    "exchange":orders.get("exch"), 
                                    "tradingsymbol":orders.get("tsym"), 
                                    "quantity":orders.get("netqty"), 
                                    "discloseqty":"0", 
                                    "price_type":"MKT",
                                    "price":"0"
                                })
                            else:
                                resp_err_data.append({"error":"quantity is greater than position","tradingsymbol":condition["tradingsymbol"],"order_type":condition["order_type"]})
        order_resp=self.place_basket(orders=place_order_data)
        order_resp=order_resp+resp_err_data
        return order_resp


