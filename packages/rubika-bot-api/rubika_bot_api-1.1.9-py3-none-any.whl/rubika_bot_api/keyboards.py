from typing import Dict, List, Any, Optional

def create_simple_keyboard(buttons: List[List[str]], resize: bool = True, on_time: bool = False) -> Dict:
    """
    Create a simple chat keypad (keyboard) structure for Rubika.

    Args:
        buttons: List of button rows, each row is a list of button texts.
                Example: [["Button1", "Button2"], ["Button3"]]
        resize (bool): If True, the keyboard is resized to fit the screen. Defaults to True.
        on_time (bool): If True, the keyboard remains visible until the user closes it. Defaults to False.

    Returns:
        Dict: The keyboard layout as a dictionary.
    
    Example:
        ```python
        keyboard = create_simple_keyboard([
            ["Button 1", "Button 2"],
            ["Button 3"]
        ])
        await bot.send_message(chat_id, "Choose:", chat_keypad=keyboard)
        ```
    """
    keyboard = {
        "rows": [],
        "resize_keyboard": resize,
        "on_time_keyboard": on_time
    }
    for row in buttons:
        keyboard["rows"].append({
            "buttons": [
                {"id": text, "type": "Simple", "button_text": text} 
                for text in row
            ]
        })
    return keyboard


class InlineKeyboardBuilder:
    """
    A helper class to easily build inline keypads using a fluent interface.
    
    This class provides a simple and intuitive way to create inline keyboards
    with various button types for Rubika bots.
    
    Example:
        ```python
        from rubika_bot_api import InlineKeyboardBuilder
        
        # Create a simple keyboard
        builder = InlineKeyboardBuilder()
        keyboard = (
            builder
            .row(
                builder.button("Click Me", "btn1"),
                builder.button("Or Me", "btn2")
            )
            .row(
                builder.button_url_link("Visit Site", "url_btn", "https://example.com")
            )
            .build()
        )
        
        # Or use static methods directly
        keyboard = (
            InlineKeyboardBuilder()
            .row(
                InlineKeyboardBuilder.button("Start", "start_btn"),
                InlineKeyboardBuilder.button_join_channel(
                    "Join Channel", "join_btn", "my_channel"
                )
            )
            .build()
        )
        ```
    """
    def __init__(self):
        """Initializes a new instance of the InlineKeyboardBuilder class."""
        self.rows: List[Dict[str, List[Dict[str, str]]]] = []

    def row(self, *buttons: Dict[str, Any]) -> 'InlineKeyboardBuilder':
        """
        Adds a new row of buttons to the keypad.

        Args:
            *buttons: Dictionaries representing the buttons to add to the row.
                     At least one button must be provided.

        Returns:
            InlineKeyboardBuilder: The builder instance for chaining.
        
        Raises:
            ValueError: If no buttons are provided.
        """
        if not buttons:
            raise ValueError("حداقل یک دکمه باید به row داده شود")
        self.rows.append({"buttons": list(buttons)})
        return self

    @staticmethod
    def button(text: str, button_id: str, button_type: str = "Simple") -> Dict[str, Any]:
        """
        Creates a dictionary for a single inline button.

        Args:
            text (str): The text that appears on the button.
            button_id (str): The ID of the button.
            button_type (str, optional): The type of the button. Defaults to "Simple".

        Returns:
            Dict[str, Any]: The inline keyboard button.
        """
        return {"id": button_id, "type": button_type, "button_text": text}
    
    @staticmethod
    def button_link(text: str, button_id: str, url: str) -> Dict[str, Any]:
        """
        Creates a dictionary for an inline URL link button.

        Args:
            text (str): The text that appears on the button.
            button_id (str): Unique identifier for the button.
            url (str): The URL that will be opened when the button is clicked.

        Returns:
            Dict[str, Any]: The inline URL link button.
        """
        return {
            "id": button_id,
            "type": "Link",
            "button_text": text,
            "button_link": {
                "type": "url",
                "link_url": url
            }
        }
    
    @staticmethod
    def button_url_link(text: str, button_id: str, url: str) -> Dict[str, Any]:
        """Alias for button_link - creates a URL link button."""
        return InlineKeyboardBuilder.button_link(text, button_id, url)
    
    @staticmethod
    def button_open_chat(text: str, button_id: str, object_guid: str, object_type: str = "User") -> Dict[str, Any]:
        """
        Creates an inline button that opens a chat.

        Args:
            text (str): The text displayed on the button.
            button_id (str): Unique identifier for the button.
            object_guid (str): The GUID of the chat/user/channel to open.
            object_type (str): Type of object ("User", "Group", "Channel"). Defaults to "User".

        Returns:
            Dict[str, Any]: The inline button for opening a chat.
        """
        return {
            "id": button_id,
            "type": "Link",
            "button_text": text,
            "button_link": {
                "type": "openchat",
                "open_chat_data": {
                    "object_guid": object_guid,
                    "object_type": object_type
                }
            }
        }
    
    @staticmethod
    def button_join_channel(text: str, button_id: str, username: str, ask_join: bool = False) -> Dict[str, Any]:
        """
        Creates an inline button that prompts the user to join a Rubika channel.

        Args:
            text (str): The text displayed on the button.
            button_id (str): Unique identifier for the button.
            username (str): The channel username (can be with or without '@').
            ask_join (bool): If True, shows confirmation dialog before joining. Defaults to False.

        Returns:
            Dict[str, Any]: The inline button for joining a channel.
        
        Example:
            ```python
            from rubika_bot_api import InlineKeyboardBuilder
            
            builder = InlineKeyboardBuilder()
            keyboard = (
                builder
                .row(
                    builder.button_join_channel(
                        text="Join Channel 📢",
                        button_id="join_btn",
                        username="my_channel",
                        ask_join=True
                    )
                )
                .build()
            )
            ```
        """
        return {
            "id": button_id,
            "type": "Link",
            "button_text": text,
            "button_link": {
                "type": "joinchannel",
                "joinchannel_data": {
                    "username": username.replace("@", ""),
                    "ask_join": ask_join
                }
            }
        } 


    @staticmethod
    def button_selection(text: str, button_id: str, selection_id: str, items: List[Dict[str, str]], title: Optional[str] = None, is_multi_selection: bool = False, columns_count: Optional[str] = None, search_type: str = "None", get_type: str = "Local") -> Dict[str, Any]:
        """
        Creates an inline selection button that opens a list of selectable items.
        Corresponds to ButtonSelection model.
        """
        button_selection_data = {
            "selection_id": selection_id,
            "items": items, # Each item is {"text": "...", "image_url": "...", "type": "TextOnly"}
            "is_multi_selection": is_multi_selection,
            "search_type": search_type,
            "get_type": get_type
        }
        if title: button_selection_data["title"] = title
        if columns_count: button_selection_data["columns_count"] = columns_count

        return {"id": button_id, "type": "Selection", "button_text": text, "button_selection": button_selection_data}

    @staticmethod
    def button_calendar(text: str, button_id: str, calendar_type: str = "DatePersian", default_value: Optional[str] = None, min_year: Optional[str] = None, max_year: Optional[str] = None, title: Optional[str] = None) -> Dict[str, Any]:
        """
        Creates an inline calendar button for date selection.
        Corresponds to ButtonCalendar model.
        """
        button_calendar_data = {"type": calendar_type}
        if default_value: button_calendar_data["default_value"] = default_value
        if min_year: button_calendar_data["min_year"] = min_year
        if max_year: button_calendar_data["max_year"] = max_year
        if title: button_calendar_data["title"] = title

        return {"id": button_id, "type": "Calendar", "button_text": text, "button_calendar": button_calendar_data}

    @staticmethod
    def button_number_picker(text: str, button_id: str, min_value: str, max_value: str, default_value: Optional[str] = None, title: Optional[str] = None) -> Dict[str, Any]:
        """
        Creates an inline number picker button for range selection.
        Corresponds to ButtonNumberPicker model.
        """
        button_number_picker_data = {
            "min_value": min_value,
            "max_value": max_value
        }
        if default_value: button_number_picker_data["default_value"] = default_value
        if title: button_number_picker_data["title"] = title

        return {"id": button_id, "type": "NumberPicker", "button_text": text, "button_number_picker": button_number_picker_data}

    @staticmethod
    def button_string_picker(text: str, button_id: str, items: List[str], default_value: Optional[str] = None, title: Optional[str] = None) -> Dict[str, Any]:
        """
        Creates an inline string picker button for selecting from a list of strings.
        Corresponds to ButtonStringPicker model.
        """
        button_string_picker_data = {"items": items}
        if default_value: button_string_picker_data["default_value"] = default_value
        if title: button_string_picker_data["title"] = title

        return {"id": button_id, "type": "StringPicker", "button_text": text, "button_string_picker": button_string_picker_data}

    @staticmethod
    def button_location(text: str, button_id: str, default_pointer_location: Optional[Dict[str, str]] = None, default_map_location: Optional[Dict[str, str]] = None, location_type: str = "Picker", title: Optional[str] = None, location_image_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Creates an inline location picker/viewer button.
        Corresponds to ButtonLocation model. default_pointer_location/default_map_location are {"latitude": "...", "longitude": "..."}
        """
        button_location_data = {"type": location_type}
        if default_pointer_location: button_location_data["default_pointer_location"] = default_pointer_location
        if default_map_location: button_location_data["default_map_location"] = default_map_location
        if title: button_location_data["title"] = title
        if location_image_url: button_location_data["location_image_url"] = location_image_url

        return {"id": button_id, "type": "Location", "button_text": text, "button_location": button_location_data}
    
    @staticmethod
    def button_textbox(text: str, button_id: str, type_line: str = "SingleLine", type_keypad: str = "String", place_holder: Optional[str] = None, title: Optional[str] = None, default_value: Optional[str] = None) -> Dict[str, Any]:
        """
        Creates an inline textbox button for text input.
        Corresponds to ButtonTextbox model.
        """
        button_textbox_data = {
            "type_line": type_line,
            "type_keypad": type_keypad
        }
        if place_holder: button_textbox_data["place_holder"] = place_holder
        if title: button_textbox_data["title"] = title
        if default_value: button_textbox_data["default_value"] = default_value

        return {"id": button_id, "type": "Textbox", "button_text": text, "button_textbox": button_textbox_data}

    @staticmethod
    def button_payment(text: str, button_id: str, amount: int, description: Optional[str] = None) -> Dict[str, Any]:
        """
        Creates an inline payment button.

        Args:
            text (str): The text displayed on the button.
            button_id (str): Unique identifier for the button.
            amount (int): Payment amount.
            description (str, optional): Payment description.

        Returns:
            Dict[str, Any]: The inline payment button.
        """
        payment_data = {
            "title": text,
            "amount": amount
        }
        if description:
            payment_data["description"] = description
        
        return {
            "id": button_id,
            "type": "Payment",
            "button_text": text,
            "button_payment": payment_data
        }

    @staticmethod
    def button_camera_image(text: str, button_id: str) -> Dict[str, Any]:
        """Creates an inline button to open camera for image capture."""
        return {"id": button_id, "type": "CameraImage", "button_text": text}

    @staticmethod
    def button_gallery_video(text: str, button_id: str) -> Dict[str, Any]:
        """Creates an inline button to open gallery for video selection."""
        return {"id": button_id, "type": "GalleryVideo", "button_text": text}
    
    @staticmethod
    def button_camera_video(text: str, button_id: str) -> Dict[str, Any]:
        """Creates an inline button to open camera for video capture."""
        return {"id": button_id, "type": "CameraVideo", "button_text": text}
    
    @staticmethod
    def button_gallery_image(text: str, button_id: str) -> Dict[str, Any]:
        """Creates an inline button to open gallery for image selection."""
        return {"id": button_id, "type": "GalleryImage", "button_text": text}
    
    @staticmethod
    def button_file(text: str, button_id: str) -> Dict[str, Any]:
        """Creates an inline button to open file picker."""
        return {"id": button_id, "type": "File", "button_text": text}
    
    @staticmethod
    def button_audio(text: str, button_id: str) -> Dict[str, Any]:
        """Creates an inline button to open audio picker."""
        return {"id": button_id, "type": "Audio", "button_text": text}
    
    @staticmethod
    def button_record_audio(text: str, button_id: str) -> Dict[str, Any]:
        """Creates an inline button to start audio recording."""
        return {"id": button_id, "type": "RecordAudio", "button_text": text}
    
    @staticmethod
    def button_my_phone_number(text: str, button_id: str) -> Dict[str, Any]:
        """Creates an inline button that shares user's phone number."""
        return {"id": button_id, "type": "MyPhoneNumber", "button_text": text}
    
    @staticmethod
    def button_my_location(text: str, button_id: str) -> Dict[str, Any]:
        """Creates an inline button that shares user's location."""
        return {"id": button_id, "type": "MyLocation", "button_text": text}
    
    @staticmethod
    def button_ask_my_phone_number(text: str, button_id: str) -> Dict[str, Any]:
        """Creates an inline button that requests user's phone number."""
        return {"id": button_id, "type": "AskMyPhoneNumber", "button_text": text}
    
    @staticmethod
    def button_ask_location(text: str, button_id: str) -> Dict[str, Any]:
        """Creates an inline button that requests user's location."""
        return {"id": button_id, "type": "AskLocation", "button_text": text}
    
    @staticmethod
    def button_barcode(text: str, button_id: str) -> Dict[str, Any]:
        """Creates an inline button to scan barcode."""
        return {"id": button_id, "type": "Barcode", "button_text": text}


    def build(self) -> Dict[str, Any]:
        """
        Finalizes and returns the constructed keyboard layout.

        Returns:
            Dict[str, Any]: The keyboard layout as a dictionary, containing rows and their button configurations.
        
        Example:
            ```python
            builder = InlineKeyboardBuilder()
            keyboard = builder.row(...).build()
            await bot.send_message(chat_id, "Choose:", inline_keypad=keyboard)
            ```
        """
        return {"rows": self.rows}
    
    def add_button(self, button: Dict[str, Any]) -> 'InlineKeyboardBuilder':
        """
        Adds a single button to the last row, or creates a new row if none exists.
        
        Args:
            button: Dictionary representing the button to add.
            
        Returns:
            InlineKeyboardBuilder: The builder instance for chaining.
        """
        if not self.rows:
            self.rows.append({"buttons": []})
        self.rows[-1]["buttons"].append(button)
        return self


class ChatKeyboardBuilder:
    """A helper class to easily build chat keypads (keyboards) using a fluent interface."""
    def __init__(self, resize: bool = True, on_time: bool = False):
        """
        Initializes a new instance of the ChatKeyboardBuilder class.

        Args:
            resize (bool): If True, the keyboard is resized to fit the screen. Defaults to True.
            on_time (bool): If True, the keyboard remains visible until the user closes it. Defaults to False.
        """
        self.rows_list: List[Dict[str, List[Dict[str, str]]]] = [] 
        self._resize = resize # CORRECTED: Assign resize
        self._on_time = on_time # CORRECTED: Assign on_time

    def row(self, *button_texts: str) -> 'ChatKeyboardBuilder':
        """
        Adds a new row of buttons to the chat keypad.

        Args:
            *button_texts: Strings representing the button texts to add to the row.
                           For chat keypads, ID and type are usually the same as text.

        Returns:
            ChatKeyboardBuilder: The builder instance for chaining.
        """
        button_list = []
        for text_val in button_texts:
            button_list.append({
                "id": text_val, 
                "type": "Simple", 
                "button_text": text_val
            })
        self.rows_list.append({"buttons": button_list})
        return self

    def build(self) -> Dict[str, Any]:
        """
        Finalizes and returns the constructed keyboard layout.

        Returns:
            Dict[str, Any]: The keyboard layout as a dictionary, containing rows and their button configurations.
        """
        return {
            "rows": self.rows_list,
            "resize_keyboard": self._resize,
            "on_time_keyboard": self._on_time
        }
    
    