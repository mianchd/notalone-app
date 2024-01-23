from ._anvil_designer import HomeFormTemplate
from anvil import *
import anvil.users

from functools import partial

from ..HomeAnonComponent import HomeAnonComponent
from ..HomeDetailComponent import HomeDetailComponent
from ..BookingComponent import BookingComponent
from ..ProfileComponent import ProfileComponent
from ..ApplicantsComponent import ApplicantsComponent
from ..MembersComponent import MembersComponent
from ..FinComponent import FinComponent
from ..VolunteerComponent import VolunteerComponent
from anvil_labs.ClientTestComponent import ClientTestComponent

from .. import Global


class HomeForm(HomeFormTemplate):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        self.link_home.add_event_handler('click', self.go_home)
        self.link_apply.add_event_handler('click', partial(self.go_page, 'apply'))
        self.link_profile.add_event_handler('click', partial(self.go_page, 'profile'))
        self.link_applicants.add_event_handler('click', partial(self.go_page, 'applicants'))
        self.link_members.add_event_handler('click', partial(self.go_page, 'members'))
        self.link_fin.add_event_handler('click', partial(self.go_page, 'financials'))
        self.link_volunteers.add_event_handler('click', partial(self.go_page, 'volunteers'))
        # self.link_forum.add_event_handler('click', partial(self.go_page, 'forum'))

        self.user = Global.user

        self.btn_test.add_event_handler('click', partial(self.go_page, 'tests'))


        
        self.set_account_state(self.user)
        self.go_home()

        from anvil.js.window import navigator
        is_mobile = anvil.js.window.navigator.userAgent.lower().find("mobi") > -1
        if is_mobile:
            self.lbl_app_title.visible = False
            self.link_forum_nav.text = ''

    def link_login_click(self, **event_args):
        """This method is called when the link is clicked"""
        Global.user = anvil.users.login_with_form(allow_cancel=True, show_signup_option=True)
        self.set_account_state(Global.user)
        self.refresh_data_bindings()
        self.go_home()

    def link_logout_click(self, **event_args):
        """This method is called when the link is clicked"""
        anvil.users.logout()
        self.set_account_state(None)
        Global.user = None  # Haven't tested this.
        self.go_home()

    def go_home(self,  **event_args):
        """This method is called when the link is clicked"""
        self.set_active_nav('home')
        if Global.user:
            self.set_account_state(Global.user)
            self.load_component(HomeDetailComponent())
        else:
            self.load_component(HomeAnonComponent())

    def require_account(self):
        user = Global.user
        if user:
            return user
        user = anvil.users.login_with_form(allow_cancel=True, show_signup_option=True)
        self.set_account_state(user)
        return user

    def set_account_state(self, user):
        self.link_logout.visible = user is not None  # TODO: remove link
        self.link_login.visible = user is None
        
        self.link_apply.visible = False
        self.link_profile.visible = False
        self.link_applicants.visible = False
        self.link_members.visible = False
        self.link_fin.visible = False
        self.link_volunteers.visible = False
        self.link_forum_nav.visible = False
        self.lbl_user.visible = False
        self.link_help.visible = False
        # self.link_forum.visible = False

        if user:
            self.lbl_user.visible = True
            self.lbl_user.text = 'Account:\n' + user['email']
            self.link_apply.visible = user['auth_booking']
            self.link_profile.visible = user['auth_profile']
            self.link_applicants.visible = user['auth_screenings']
            self.link_members.visible = user['auth_members']
            self.link_fin.visible = user['auth_members']
            self.link_volunteers.visible = user['auth_members']
            self.link_forum_nav.visible = (
                user['auth_forumchat'] == True and
                user['first_name'] != '' and
                user['last_name'] != ''
            )
            # self.link_forum.visible = user['auth_members']  # TODO: Change later.
            self.btn_test.visible = user['auth_dev']
            # self.tb_impersonate.visible = user['auth_dev']
            
            if user['tenant']:
                self.lbl_app_title.text = user['tenant']['name']
                self.link_help.visible = True
                

    def load_component(self, cmpt):
        self.cmpt = cmpt
        self.content_panel.clear()
        self.content_panel.add_component(cmpt)
        cmpt.add_event_handler('x-refresh', self.refresh_everything)
        cmpt.add_event_handler('x-go-home', self.go_home)

    def set_active_nav(self, state):
        self.link_home.role = 'selected' if state == 'home' else None
        self.link_apply.role = 'selected' if state == 'apply' else None
        self.link_profile.role = 'selected' if state == 'profile' else None
        self.link_applicants.role = 'selected' if state == 'applicants' else None
        self.link_members.role = 'selected' if state == 'members' else None
        self.link_fin.role = 'selected' if state == 'financials' else None
        self.link_volunteers.role = 'selected' if state == 'volunteers' else None
        # self.link_forum.role = 'selected' if state == 'forum' else None

    def go_page(self, page_name, **event_args):
        """Go to a page."""
        self.set_active_nav(page_name)
        user = self.require_account()
        if page_name == 'apply' and user:
            self.load_component(BookingComponent())
        elif page_name == 'profile' and user:
            self.load_component(ProfileComponent())
        elif page_name == 'applicants' and user:
            self.load_component(ApplicantsComponent())
        elif page_name == 'members' and user:
            self.load_component(MembersComponent())
        elif page_name == 'financials' and user:
            self.load_component(FinComponent())
        elif page_name == 'volunteers' and user:
            self.load_component(VolunteerComponent())
        # elif page_name == 'forum' and user:
            # self.load_component(ForumiComponent())
            # self.cmpt.form_show()
        elif page_name == 'tests' and user:
            self.tb_impersonate.visible = True
            from .. import test_forms, test_server, test_tasks
            self.load_component(
                ClientTestComponent(
                    test_modules=[test_forms, test_server, test_tasks],
                    card_roles=['tonal-card', 'elevated-card', 'elevated-card'],
                    icon_size=30,
                    btn_role='filled-button',
                )
            )

    def refresh_everything(self, **event_args):
        """Refresh mainly the menu links."""
        self.user = Global.user
        self.set_account_state(self.user)
        self.refresh_data_bindings()

    def link_forum_nav_click(self, **event_args):
        """This method is called when the link is clicked"""
        anvil.js.window.location.href = Global.forumlink

    def link_help_click(self, **event_args):
        """This method is called when the link is clicked"""
        if self.user and self.user['tenant']:
            alert('For help, contact ' + self.user['tenant']['email'])

    def tb_impersonate_pressed_enter(self, **event_args):
        """This method is called when the user presses Enter in this text box"""
        self.user = anvil.server.call('impersonate_user', self.tb_impersonate.text)
        # reset the globals
        Global.clear_global_attributes()
        Global.user = self.user
        self.refresh_everything()
        self.go_home()
