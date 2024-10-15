from odoo import models, fields, api, SUPERUSER_ID

class RecruitmentRequest(models.Model):
    _name = 'recruitment.request'
    _description = 'Recruitment Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Number', required=True, copy=False, readonly=True, default='New')
    requester_id = fields.Many2one('res.users', string='Requester', required=True, default=lambda self: self.env.user)
    manager_id = fields.Many2one('res.users', string='Approval Manager', required=True)
    department_id = fields.Many2one('hr.department', string='Department', required=True)
    job_position = fields.Many2one('hr.job', string='Job Position', required=True)
    job_title = fields.Char(string='Job Title')
    number_of_employees = fields.Integer(string='Number of Employees', required=True, default=1)
    description = fields.Text(string='Description')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('done', 'Done')
    ], string='Status', default='draft')
    expected_date = fields.Date(string='Expected Date', required=True,)
    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('very_high', 'Very High')
    ], string='Priority', required=True, default='medium')

    hr_responsible_user_ids = fields.Many2many('res.users', compute='_compute_hr_responsible_user_ids', string='HR Responsible Users')

    @api.depends('department_id')
    def _compute_hr_responsible_user_ids(self):
        hr_responsible_users = self.env['hr.employee'].search([('hr_responsible', '=', True)]).mapped('user_id')
        self.hr_responsible_user_ids = hr_responsible_users

    @api.model
    def create(self, vals):
        if vals.get('number_of_employees', 0) == 0:
            vals['number_of_employees'] = 1
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('recruitment.request') or 'New'
        return super(RecruitmentRequest, self).create(vals)
    
    def write(self, vals):
        if 'number_of_employees' in vals and vals['number_of_employees'] == 0:
            vals['number_of_employees'] = 1
        return super(RecruitmentRequest, self).write(vals)

    def action_submit(self):
        self.state = 'submitted'
        # Send email to manager for approval
        template = self.env.ref('recruitment_request.mail_template_recruitment_request')
        self.env['mail.template'].browse(template.id).send_mail(self.id, force_send=True)

    def action_approve(self):
        self.state = 'approved'
        job_position = self.job_position
        if job_position:
            # Update the job_position fields with values from the recruitment request
            job_position.write({
                'department_id': self.department_id.id,
                'no_of_recruitment': self.number_of_employees,
                'user_id': self.manager_id.id,
                'description': self.description,
                'state': 'recruit'  # Set the state to 'recruit' to make the job position visible
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
