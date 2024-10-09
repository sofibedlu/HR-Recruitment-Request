from odoo import models, fields, api

class RecruitmentRequest(models.Model):
    _name = 'recruitment.request'
    _description = 'Recruitment Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Request Title', required=True)
    requester_id = fields.Many2one('res.users', string='Requester', required=True, default=lambda self: self.env.user)
    manager_id = fields.Many2one('res.users', string='Approval Manager', required=True)
    department_id = fields.Many2one('hr.department', string='Department', required=True)
    job_position = fields.Char(string='Job Position', required=True)
    job_title = fields.Char(string='Job Title', required=True)
    number_of_employees = fields.Integer(string='Number of Employees', required=True)
    description = fields.Text(string='Description')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('done', 'Done')
    ], string='Status', default='draft')

    def action_submit(self):
        self.state = 'submitted'
        # Send email to manager for approval
        template = self.env.ref('recruitment_request.mail_template_recruitment_request')
        self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True)

    def action_approve(self):
        self.state = 'approved'
        # Create recruitment/job position
        self.env['hr.job'].create({
            'name': self.job_position,
            'department_id': self.department_id.id,
            'description': self.description,
        })
        # Send email to requester about approval
        template = self.env.ref('recruitment_request.mail_template_recruitment_approved')
        self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True)

    def action_reject(self):
        self.state = 'rejected'
        # Send email to requester about rejection
        template = self.env.ref('recruitment_request.mail_template_recruitment_rejected')
        self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True)

    def action_done(self):
        self.state = 'done'