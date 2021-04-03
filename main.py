from kivy.core.window import Window
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivymd.uix.floatlayout import MDFloatLayout
from kivy.uix.popup import Popup
from kivy.uix.recycleview import RecycleView
from kivymd.app import MDApp
from kivymd.uix.list import OneLineListItem
from kivymd.uix.tab import MDTabsBase
from kivy.properties import ListProperty
import pandas as pd
from datetime import datetime
import pyrebase


Window.size = (300, 500)

products = []

pr_items = []

tr_items = []

class RV(RecycleView):
    rv_products = ListProperty(
        [{'sku': str(x['SKU']), 'pr_name': str(x['PR_name']), 'pr_price': x['PR_price']} for x in pr_items])


class RVH(RecycleView):
    rvh_transactions = ListProperty(
        [{'trans_date': str(t['TRANS_DATE']), 'trans_user': str(t['TRANS_USER']), 'trans_sum': str(t['TRANS_SUM'])} for
         t in tr_items])
class Tab(MDFloatLayout, MDTabsBase):
    '''Class implementing content for a tab.'''
    pass


class TableBasket(BoxLayout):
    pass


class TableHistory(BoxLayout):
    pass


class MyLayout(BoxLayout):
    scr_mngr = ObjectProperty(None)

    def change_screen(self, screen, *args):
        self.scr_mngr.current = screen


class OpenDialog(Popup):
    pass


class MenuOSApp(MDApp):


    config = {
        "apiKey": "apiKey",
        "authDomain": "kivymos.firebaseapp.com",
        "databaseURL": "https://kivymos-default-rtdb.firebaseio.com/",
        "storageBucket": "kivymos.appspot.com"
    }
    firebase_app = pyrebase.initialize_app(config)

    def __init__(self, items=[], list_items=[]):
        MDApp.__init__(self)
        self.items = items
        self.list_items = list_items

    def on_start(self):

        self.show_transaction_history()
        return MyLayout()



    def on_tab_switch(
            self, instance_tabs, instance_tab, instance_tab_label, tab_text
    ):
        pass

    def show_MDDialog(self, card_id):
        dlg = OpenDialog(title=card_id)
        dlg.open()

    def show_MDInput(self):
        pass

    def show_items(self):
        self.root.ids.container.clear_widgets()
        for i in range(len(products)):
            self.root.ids.container.add_widget(
                OneLineListItem(text=f"{products[i]}")
            )

    def impulse_item_clicked(self, values={}):

        products.append(values)

        self.root.ids.rv.rv_products.append(
            {'sku': values.get('sku'), 'pr_name': values.get('pr_name'), 'pr_price': values.get('pr_price')})

        basket_items = self.root.ids.rv.rv_products
        df = pd.DataFrame(basket_items)

        convert_rv_products = {'sku': int, 'pr_name': str, 'pr_price': float}

        df = df.astype(convert_rv_products)


        self.root.ids.basket_sum_text.text = "Sum : " + str("%.2f" % df.pr_price.sum())


    def close_spinner(self, id):
        pass


    def spinner_values(self, values=[]):
        pass




    def pay_basket(self):

        now = datetime.now()
        dt_string = now.strftime("%Y-%m-%d %H:%M:%S")


        basket_items = self.root.ids.rv.rv_products
        df = pd.DataFrame(basket_items)

        convert_rv_products = {'sku': int, 'pr_name': str, 'pr_price': float}
        df = df.astype(convert_rv_products)

        db = self.firebase_app.database()
        user_name = 'Soyut'
        basket_items_with_sum = {"Username" : user_name, "Sum": float("%.2f" % df.pr_price.sum()), "Items": basket_items}

        results = db.child(dt_string).set(basket_items_with_sum)

        self.root.ids.rv.rv_products = {}

        self.send_transaction_email(basket_items)
        self.root.ids.basket_sum_text.text = ""
        self.show_transaction_history()

    # send transactions as an email
    def send_transaction_email(self, basket_items):
        message = ""
        for item in basket_items:
            message += item['pr_name'] + " - " + item['pr_price'] + "\n"

    def show_transaction_history(self):
        db_history2 = self.firebase_app.database().get()

        tr_user = ""
        tr_sum = ""
        for hist in db_history2.each():
            tr_date = hist.key()

            for h in hist.val().items():
                if h[0] == "Username":
                    tr_user = h[1]
                if h[0] == "Sum":
                    tr_sum = h[1]

            self.root.ids.rvh.rvh_transactions.append(
                {'trans_date': str(tr_date), 'trans_user': str(tr_user), 'trans_sum': str(tr_sum)})


if __name__ == '__main__':
    MenuOSApp().run()
