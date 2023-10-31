import flet as ft
import openai
openai_api_key = "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"
openai.api_key = openai_api_key 

class Message():
    def __init__(self, user: str, text: str, message_type: str):
        self.user = user
        self.text = text
        self.message_type = message_type



def main(page: ft.Page):

    user_name = ft.TextField(label="Usuario")

    def join_click(e):
        if not user_name.value:
            user_name.error_text = "Name cannot be blank!"
            user_name.update()
        else:
            page.session.set("user_name", user_name.value)
            page.views.pop()
            top_view = page.views[-1]
            page.go(top_view.route)
            page.pubsub.send_all(Message(user=user_name.value, text=f"Te has identificado correctamente como: {user_name.value}", message_type="login_message"))
            page.update()

    def check_item_clicked(e):
            e.control.checked = not e.control.checked
            page.update()

    def button_clicked(e):
        page.update()
    
    def consulta_gpt(promt_user, promt_system=""):
        completion = openai.ChatCompletion.create(
            model='gpt-4',
            messages=[
            {"role": "system", "content": promt_system},
            {"role": "user", "content": promt_user}
            ]
        )
        salida = completion["choices"][0]["message"]["content"]
        page.pubsub.send_all(Message(user="ChatGPT", text=salida, message_type="chat_message"))
  

    def handle_route_change(r: ft.RouteChangeEvent):
        """
        Called whenever the page's/app's route changes.
        It checks if the new route matches that of the full-screen dialog("/full").
        If it's the case, it adds the corresponding view to the page.
        """
        if page.route == "/full":
            page.views.append(
                ft.View(
                    route="/full",
                    fullscreen_dialog=True,     # MAIN parameter for the full-screen dialog!
                    appbar=ft.AppBar(title=ft.Text("Mi perfil"),),
                    controls=[user_name,ft.TextField(label="Contraseña"), ft.ElevatedButton(text="Join chat", on_click=join_click)]
                )
            )
            page.update()

        
    def handle_view_pop(view: ft.ViewPopEvent):
        """
        Fired when the user clicks the "Close" button in the AppBar.
        The uppermost view is popped/removed from the views collection and
        the page's current route is updated to match that of the view "under" it.
        """
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)
    
    def show_dialog(e: ft.ControlEvent):
        """Called on click of the 'show' button. Opens the view with the full-screen dialog."""
        page.go("/full")
        page.update()

    # set our handles/callbacks defined above
    page.on_route_change = handle_route_change
    page.on_view_pop = handle_view_pop


    page.appbar = ft.AppBar(
        leading=ft.Icon(ft.icons.CHAT),
        leading_width=40,
        title=ft.Text("Chat JT 0.1"),
        center_title=False,
        bgcolor=ft.colors.SURFACE_VARIANT,
        actions=[
            ft.IconButton(ft.icons.PERSON_ADD, on_click=show_dialog),
        ],
    )

    
    chat = ft.Column()
    new_message = ft.TextField()

    def on_message(message: Message):
        if message.message_type == "chat_message":
            chat.controls.append(ft.Text(f"{message.user}: {message.text}"))
        elif message.message_type == "login_message":
            chat.controls.append(
                ft.Text(message.text, italic=True, color=ft.colors.BLACK45, size=12)
            )
        page.update()

    page.pubsub.subscribe(on_message)

    def send_click(e):
        page.pubsub.send_all(Message(user=page.session.get('user_name'), text=new_message.value, message_type="chat_message"))
        consulta_gpt(new_message.value)
        new_message.value = ""
        page.update()

    

  

    page.add(chat, ft.Row([new_message, ft.ElevatedButton("Send", on_click=send_click)]))

ft.app(target=main, view=ft.WEB_BROWSER)