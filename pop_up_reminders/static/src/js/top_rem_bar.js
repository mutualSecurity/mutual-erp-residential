openerp.pop_up_reminders = function(instance){
"use strict";

var core = instance.web.core;
var SystrayMenu = instance.web.Menu;
var Widget = instance.web.Widget;
var QWeb = instance.web.qweb;
var ajax = instance.web.ajax;

var reminder_menu = Widget.extend({
    template:'pop_up_reminders.reminder_menu',

    events: {
        "click .dropdown-toggle": "on_click_reminder",
        "click .detail-client-address-country": "reminder_active",
    },

    init:function(parent, name){
        this.reminder = null;
        this._super(parent);
    },

    on_click_reminder: function (event) {
        var self = this
         ajax.jsonRpc("/pop_up_reminders/all_reminder", 'call',{}
        ).then(function(all_reminder){
        self.all_reminder = all_reminder
         /*console.log(self.all_reminder);*/
        self.$('.o_mail_navbar_dropdown_top').html(QWeb.render('pop_up_reminders.reminder_menu',{
                values: self.all_reminder
            }));
        })
        },


    reminder_active: function(){
        var self = this;
        var value =$("#reminder_select").val();
        ajax.jsonRpc("/pop_up_reminders/reminder_active", 'call',{'reminder_name':value}
        ).then(function(reminder){
            console.log(self);
            self.reminder = reminder
             for (var i=0;i<1;i++){
                    var model = self.reminder[i]
                    var date = self.reminder[i+1]
                    if (self.reminder[i+2] == 'today'){
                        return self.do_action({
                             type: 'ir.actions.act_window',
                            res_model: model,
                            view_mode: 'tree',
                            view_type: 'tree',
                            domain: [[date, '=', new Date()]],
                            views: [[false, 'tree']],
                            target: 'new',})
                        }

                    else if (self.reminder[i+2] == 'set_date'){
                        return self.do_action({
                            type: 'ir.actions.act_window',
                            res_model: model,
                            view_mode: 'tree',
                            view_type: 'tree',
                            domain: [[date, '=', self.reminder[i+3]]],
                            views: [[false, 'tree']],
                            target: 'new',})
                        }
                        
                    else if (self.reminder[i+2] == 'set_period'){

                        return self.do_action({
                            type: 'ir.actions.act_window',
                            res_model: model,
                            view_mode: 'tree',
                            view_type: 'tree',
                            domain: [[date, '<', self.reminder[i+5]],[date, '>', self.reminder[i+4]]],
                            views: [[false, 'tree']],
                            target: 'new',})
                            }

                        }

             });
        },
});
console.log("Web Object")
console.log(instance.web.Menu.Scopes)
SystrayMenu.Items.push(reminder_menu);
};
