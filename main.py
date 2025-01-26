from tkinter import Label, Button

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from firebase_service import FirebaseService
from kivymd.uix.list import OneLineListItem
import firebase_admin
from firebase_admin import credentials
firebase_service = FirebaseService()

# Load Kivy layout files
Builder.load_file('kivy/login.kv')
Builder.load_file('kivy/signup.kv')
Builder.load_file('kivy/home.kv')
Builder.load_file('kivy/search.kv')
Builder.load_file('kivy/add_post.kv')
Builder.load_file('kivy/community.kv')
Builder.load_file('kivy/profile.kv')
Builder.load_file('kivy/messages.kv')
Builder.load_file('kivy/notifications.kv')

# Screens
class LoginScreen(Screen):
    def login(self):
        username = self.ids.username.text
        password = self.ids.password.text
        if firebase_service.authenticate_user(username, password):
            self.manager.current = 'home'
        else:
            self.ids.error_message.text = "Invalid credentials. Try again."

class SignupScreen(Screen):
    def signup(self):
        username = self.ids.username.text
        email = self.ids.email.text
        password = self.ids.password.text
        firebase_service.add_user(username, email, password)
        self.manager.current = 'login'

class HomeScreen(Screen):
    def on_enter(self):
        posts = firebase_service.get_posts()
        self.ids.posts_container.text = "\n".join([f"{post['content']}" for post in posts])

class SearchScreen(Screen):
    def perform_search(self):
        query = self.ids.search_input.text
        # Simulate search logic. Replace with Firestore query.
        results = firebase_service.search(query)
        results_container = self.ids.search_results
        results_container.clear_widgets()

        for result in results:
            results_container.add_widget(Label(text=result))


class AddPostScreen(Screen):
    def create_post(self):
        content = self.ids.post_content.text
        anonymous = self.ids.anonymous.active
        firebase_service.add_post(content, anonymous)
        self.manager.current = 'home'


class CommunityScreen(Screen):
    def on_enter(self):
        communities = firebase_service.get_communities()
        community_list = self.ids.community_list
        community_list.clear_widgets()

        for community in communities:
            btn = Button(text=community['name'])
            btn.bind(on_release=lambda x, c=community: self.join_community(c))
            community_list.add_widget(btn)

    def create_community(self):
        # Navigate to a "Create Community" page or display a popup
        pass

    def join_community(self, community):
        firebase_service.join_community(community)


class ProfileScreen(Screen):
    def on_enter(self):
        profile_data = firebase_service.get_user_profile()
        self.ids.username.text = profile_data['username']
        self.ids.followers.text = f"Followers: {profile_data['followers']}"
        self.ids.following.text = f"Following: {profile_data['following']}"

        posts = firebase_service.get_user_posts()
        posts_container = self.ids.posts_container
        posts_container.clear_widgets()

        for post in posts:
            posts_container.add_widget(Label(text=post['content']))


class MessagesScreen(Screen):
    def on_enter(self):
        messages = firebase_service.get_messages()
        message_list = self.ids.message_list
        message_list.clear_widgets()

        for message in messages:
            message_list.add_widget(Label(text=f"{message.get('sender', 'Unknown')}: {message.get('content', 'No content')}"))


class NotificationsScreen(Screen):
    def on_enter(self):
        notifications = firebase_service.get_notifications()
        notification_list = self.ids.notification_list
        notification_list.clear_widgets()

        for notification in notifications:
            notification_list.add_widget(OneLineListItem(text=notification['message']))

class FirebaseService:
    def __init__(self, cred_path):
        try:
            # Initialize Firebase with the credentials path
            self.cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(self.cred)
            print("Firebase initialized successfully")
        except Exception as e:
            print(f"Error initializing Firebase: {e}")


# Main App
class SocialMediaApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(SignupScreen(name='signup'))
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(SearchScreen(name='search'))
        sm.add_widget(AddPostScreen(name='add_post'))
        sm.add_widget(CommunityScreen(name='community'))
        sm.add_widget(ProfileScreen(name='profile'))
        sm.add_widget(MessagesScreen(name='messages'))
        sm.add_widget(NotificationsScreen(name='notifications'))
        return sm

if __name__ == '__main__':
    SocialMediaApp().run()
