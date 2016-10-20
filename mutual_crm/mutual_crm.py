from openerp import models,fields, api

class crm_lead(models.Model):
    _inherit = "crm.lead"

    def log_next_activity_done(self, cr, uid, ids, context=None, next_activity_name=False):
        stages_leads = {}
        for lead in self.browse(cr, uid, ids, context=context):
            stage_id = self.stage_find(cr, uid, [lead], lead.section_id.id or False,
                                       [('probability', '=', 70.00), ('on_change', '=', True)], context=context)
            if stage_id:
                if stages_leads.get(stage_id):
                    stages_leads[stage_id].append(lead.id)
                else:
                    stages_leads[stage_id] = [lead.id]
            else:
                raise osv.except_osv(_('Warning!'),
                                     _(
                                         'To relieve your sales pipe and group all Won opportunities, configure one of your sales stage as follow:\n'
                                         'probability = 100 % and select "Change Probability Automatically".\n'
                                         'Create a specific stage or edit an existing one by editing columns of your opportunity pipe.'))
        for stage_id, lead_ids in stages_leads.items():
            self.write(cr, uid, lead_ids, {'stage_id': stage_id}, context=context)
        return True



        crm_lead()
class survey_schdule_lead(models.Model):
    _inherit = "crm.lead"
    def survey_schedule(self, cr, uid, ids, context=None, next_activity_name=False):
        stages_leads = {}
        for lead in self.browse(cr, uid, ids, context=context):
            stage_id = self.stage_find(cr, uid, [lead], lead.section_id.id or False,
                                       [('probability', '=', 40.00), ('on_change', '=', True)], context=context)
            if stage_id:
                if stages_leads.get(stage_id):
                    stages_leads[stage_id].append(lead.id)
                else:
                    stages_leads[stage_id] = [lead.id]
            else:
                raise osv.except_osv(_('Warning!'),
                                     _(
                                         'To relieve your sales pipe and group all Won opportunities, configure one of your sales stage as follow:\n'
                                         'probability = 100 % and select "Change Probability Automatically".\n'
                                         'Create a specific stage or edit an existing one by editing columns of your opportunity pipe.'))
        for stage_id, lead_ids in stages_leads.items():
            self.write(cr, uid, lead_ids, {'stage_id': stage_id}, context=context)
        return True
