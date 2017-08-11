from openerp.osv import fields, osv
from openerp import models
from openerp import fields as field
from openerp import api


class AccountInventory(osv.osv):
    _name = 'inventory.logs'
    _columns = {
        'item_code': fields.integer('Item Code', store=True),
        'item_name': fields.char('Item Name',store=True),
        'sale_return': fields.float('Sale Return',store=True),
        'purchase_return': fields.float('Purchase Return',store=True),
        'purchase_count': fields.float('Receipt', store=True),
        'sale_count': fields.float('Sales', store=True),
        'date': fields.date('Date', store=True),
    }


class Inventory(osv.osv):
    _name = 'inventory.accounts'
    _columns = {
        'item_code': fields.integer('Item Code', store=True),
        'item_name': fields.char('Item Name', store=True),
    }


class InventoryOpening(osv.osv):
    _name = 'inventory.opening'
    _columns = {
        'item_code': fields.integer('Item Code', store=True),
        'item_name': fields.char('Item Name', store=True),
        'opening_count': fields.float('Opening',store=True),
        'date': fields.date('Date', store=True),
    }