from pyodide.http import pyfetch
from js import console, XMLHttpRequest
import asyncio
import base64
import json
import smtplib
from functools import partial

current_quote = ""
current_author = ""
selected_quotes_list = []


async def get_quote(*args, **kwargs):
    quote_response = await pyfetch(url="http://api.quotable.io/random", method="GET")
    quote_data = await quote_response.json()

    global current_quote, current_author
    current_quote = quote_data['content']
    current_author = quote_data['author']

    quote = '"' + quote_data['content'] + '"' + " - " + quote_data['author']
    pyscript.write('quote', quote)
    try:
        celebrity = quote_data['author']
        wikipedia_url = f"https://en.wikipedia.org/w/api.php?origin=*&action=query&prop=pageimages&format=json&piprop=original&titles={celebrity}"
        wiki_response = await pyfetch(url=wikipedia_url, method="GET", headers={"Content-Type": "application/json"});
        wiki_data = await wiki_response.json()

        PAGES = wiki_data['query']['pages']
        for page in PAGES:
            image_file = PAGES[page]['original']['source']

        image_element = Element('author');
        image_element.element.src = image_file
    except:
        image_element = Element('author');
        image_element.element.src = 'https://www.ncenet.com/wp-content/uploads/2020/04/no-image-png-2.png'


await get_quote()


def delete_selected_quote(id, *args, **kwargs):
    global selected_quotes_list
    element_to_delete = Element("quote-" + str(id))
    element_to_delete.element.remove()
    selected_quotes_list = [quote for quote in selected_quotes_list if quote.get('id') == id]


def set_request_status(message):
    request_status = Element('request-status')
    request_status.element.innerText = message


def add_quote_button(*args, **kwargs):
    global selected_quotes_list
    selected_quote = {"id": len(selected_quotes_list),
                      "author": current_author,
                      "quote": current_quote
                      }
    if len(selected_quotes_list) > 0:
        for quote in selected_quotes_list:
            if quote.get('quote') == selected_quote.get('quote'):
                return
    set_request_status('')


    selected_quotes_list.append(selected_quote)
    quotes_to_send = Element('selected_quotes_list')
    single_quote_card = create('div',
                               classes="grid grid-cols-8 quote_card hover:bg-gray-200 cursor-pointer transition-all ease-in-out duration-150 px-3 py-1")
    single_quote_card.element.id = "quote-" + str(selected_quote.get("id"))
    single_quote_text = create('div', classes="col-span-7 whitespace-nowrap three-dots")
    single_quote_text.element.innerText = selected_quote.get("author") + ' - "' + selected_quote.get("quote") + '"'
    single_quote_delete_icon = create('span', classes="material-symbols-outlined col-span-1"
                                                      " text-center text-white quote_delete_icon "
                                                      "text-right transition-colors duration-150 ease-in-out "
                                                      "pointer-events-none")
    single_quote_delete_icon.element.onclick = partial(delete_selected_quote, selected_quote.get("id"))
    single_quote_delete_icon.element.innerText = "delete"
    single_quote_card.element.appendChild(single_quote_text.element)
    single_quote_card.element.appendChild(single_quote_delete_icon.element)
    quotes_to_send.element.appendChild(single_quote_card.element)


def email_sent(e):
    global selected_quotes_list
    for quote in selected_quotes_list:
        element_to_delete = Element("quote-" + str(quote.get('id')))
        element_to_delete.element.remove()
    selected_quotes_list = []
    set_request_status('Email sent successfully')


def email_failed(e):
    set_request_status("I couldn't send you the email")


async def send_email(*args, **kwargs):
    global selected_quotes_list
    set_request_status('Sending the email')
    receiver_email = Element('email_input').element.value
    req = XMLHttpRequest.new()
    data = {"email": receiver_email, "quotes": selected_quotes_list}
    req.open("POST", "http://127.0.0.1:5000/send-email", True)
    req.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');

    req.send(data)
    req.onload = email_sent
    req.onerror = email_failed
