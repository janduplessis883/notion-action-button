from notion_client import Client
import pprint
import pandas as pd
import streamlit as st

my_notion_token = st.secrets["notion"]["token"]

class NotionHelper:
    """
    Class NotionHelper
    ------------------
    A class to assist in interfacing with the Notion API.

    Methods:
    - __init__(self): Initializes an instance of the class and invokes the authenticate method.
    - authenticate(self): Sets the `notion_token` property equal to the `ac.notion_api_key` and creates a `Client` instance with the `notion_token` property to be used for queries.
    - notion_search_db(self, database_id='e18e2d110f9e401eb1adf3190e51a21b', query=''): Queries a Notion database and returns the page title and url of the result(s) page. If there are multiple results, pprint module is used to pretty print the results.
    - notion_get_page(self, page_id): Retrieves a Notion page and returns the heading and an array of blocks on that page.
    - create_database(self, parent_page_id, database_title, properties): Creates a new database in Notion.
    - new_page_to_db(self, database_id, page_properties): Adds a new page to a Notion database.
    - append_page_body(self, page_id, blocks): Appends blocks of text to the body of a Notion page.
    - get_all_page_ids(self, database_id): Returns the IDs of all pages in a given database.
    - get_all_pages_as_json(self, database_id): Returns a list of JSON objects representing all pages in the given database, with all properties.

    Usage:
    - Instantiate a `NotionHelper` object.
    - Call the `notion_search_db` method to search for pages in a Notion database.
    - Call the `notion_get_page` method to retrieve a page and its blocks.
    - Call the `create_database` method to create a new database in Notion.
    - Call the `new_page_to_db` method to add a new page to a Notion database.
    - Call the `append_page_body` method to append blocks of text to a Notion page.
    - Call the `get_all_page_ids` method to get the IDs of all pages in a database.
    - Call the `get_all_pages_as_json` method to get all pages as JSON objects.
    """

    def __init__(self):
        self.authenticate()

    def authenticate(self):
        # Authentication logic for Notion
        self.notion_token = my_notion_token
        self.notion = Client(auth=self.notion_token)

    def get_database(self, database_id):
        # Fetch the database schema
        response = self.notion.databases.retrieve(database_id=database_id)
        return response

    def notion_search_db(
        self, database_id="e18e2d110f9e401eb1adf3190e51a21b", query=""
    ):
        my_pages = self.notion.databases.query(
            **{
                "database_id": database_id,
                "filter": {
                    "property": "title",
                    "rich_text": {
                        "contains": query,
                    },
                },
            }
        )

        page_title = my_pages["results"][0]["properties"][
            "Code / Notebook Description"
        ]["title"][0]["plain_text"]
        page_url = my_pages["results"][0]["url"]

        page_list = my_pages["results"]
        count = 1
        for page in page_list:
            try:
                print(
                    count,
                    page["properties"]["Code / Notebook Description"]["title"][0][
                        "plain_text"
                    ],
                )
            except IndexError:
                print("No results found.")

            print(page["url"])
            print()
            count = count + 1

        # pprint.pprint(page)

    def notion_get_page(self, page_id):
        """Returns the heading and an array of blocks on a Notion page given its page_id."""

        page = self.notion.pages.retrieve(page_id)
        blocks = self.notion.blocks.children.list(page_id)
        heading = page["properties"]["Subject"]["title"][0]["text"]["content"]
        content = [block for block in blocks["results"]]

        print(heading)
        return content

    def create_database(self, parent_page_id, database_title, properties):
        """Creates a new database in Notion."""

        # Define the properties for the database
        new_database = {
            "parent": {"type": "page_id", "page_id": parent_page_id},
            "title": [{"type": "text", "text": {"content": database_title}}],
            "properties": properties,
        }

        response = self.notion.databases.create(**new_database)
        return response

    def new_page_to_db(self, database_id, page_properties):
        """Adds a new page to a Notion database."""

        new_page = {
            "parent": {"database_id": database_id},
            "properties": page_properties,
        }

        response = self.notion.pages.create(**new_page)
        return response

    def append_page_body(self, page_id, blocks):
        """Appends blocks of text to the body of a Notion page."""

        new_blocks = {"children": blocks}

        response = self.notion.blocks.children.append(block_id=page_id, **new_blocks)
        return response

    def get_all_page_ids(self, database_id):
        """Returns the IDs of all pages in a given database."""

        my_pages = self.notion.databases.query(database_id=database_id)
        page_ids = [page["id"] for page in my_pages["results"]]
        return page_ids

    def get_all_pages_as_json(self, database_id):
        """Returns a list of JSON objects representing all pages in the given database, with all properties."""

        my_pages = self.notion.databases.query(database_id=database_id)
        pages_json = [page["properties"] for page in my_pages["results"]]
        return pages_json

    def get_all_pages_as_dataframe(self, database_id):
        """Returns a Pandas DataFrame representing all pages in the given database, with selected properties."""

        pages_json = self.get_all_pages_as_json(database_id)
        data = []

        # Define the list of allowed property types that we want to extract
        allowed_properties = ["title", "status", "number", "date", "url", "checkbox", "rich_text", "email", "select"]

        for page in pages_json:
            row = {}
            for key, value in page.items():
                property_type = value.get("type", "")

                if property_type in allowed_properties:
                    if property_type == "title":
                        row[key] = value.get("title", [{}])[0].get("plain_text", "")
                    elif property_type == "status":
                        row[key] = value.get("status", {}).get("name", "")
                    elif property_type == "number":
                        row[key] = value.get("number", "")
                    elif property_type == "date":
                        date_field = value.get("date", {})
                        row[key] = date_field.get("start", "") if date_field else ""
                    elif property_type == "url":
                        row[key] = value.get("url", "")
                    elif property_type == "checkbox":
                        row[key] = value.get("checkbox", False)
                    elif property_type == "rich_text":
                        rich_text_field = value.get("rich_text", [])
                        row[key] = rich_text_field[0].get("plain_text", "") if rich_text_field else ""
                    elif property_type == "email":
                        row[key] = value.get("email", "")
                    elif property_type == "select":
                        select_field = value.get("select", {})
                        row[key] = select_field.get("name", "") if select_field else ""

            data.append(row)

        df = pd.DataFrame(data)
        # Prevent numbers from displaying in scientific notation
        pd.options.display.float_format = '{:.0f}'.format
        return df


# Usage example:
# parent_page_id = "your_parent_page_id"
# database_title = "My New Database"
# properties = {
#     "Name": {
#         "title": {}
#     },
#     "Date": {
#         "date": {}
#     },
#     "Email Count": {
#         "number": {}
#     }
# }

# notion_helper = NotionHelper()
# notion_helper.create_database(parent_page_id, database_title, properties)

# # Assuming the database was created and you have its ID
# database_id = "your_database_id"

# page_properties = {
#     "Name": {
#         "title": [
#             {
#                 "text": {
#                     "content": "Example Page"
#                 }
#             }
#         ]
#     },
#     "Date": {
#         "date": {
#             "start": "2024-08-01"
#         }
#     },
#     "Email Count": {
#         "number": 10
#     }
# }

# notion_helper.new_page_to_db(database_id, page_properties)

# # Assuming the page was created and you have its ID
# page_id = "your_page_id"

# blocks = [
#     {
#         "object": "block",
#         "type": "paragraph",
#         "paragraph": {
#             "text": [
#                 {
#                     "type": "text",
#                     "text": {
#                         "content": "This is the first paragraph of text."
#                     }
#                 }
#             ]
#         }
#     },
#     {
#         "object": "block",
#         "type": "paragraph",
#         "paragraph": {
#             "text": [
#                 {
#                     "type": "text",
#                     "text": {
#                         "content": "This is the second paragraph of text."
#                     }
#                 }
#             ]
#         }
#     }
# ]

# notion_helper.append_page_body(page_id, blocks)
