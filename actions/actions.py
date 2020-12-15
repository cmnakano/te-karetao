from typing import Any, Text, Dict, List, Optional

from rasa_sdk.knowledge_base.utils import (
    SLOT_OBJECT_TYPE,
    SLOT_LAST_OBJECT_TYPE,
    SLOT_ATTRIBUTE,
    reset_attribute_slots,
    SLOT_MENTION,
    SLOT_LAST_OBJECT,
    SLOT_LISTED_OBJECTS,
    get_object_name,
    get_attribute_slots,
)

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.knowledge_base.storage import InMemoryKnowledgeBase
from rasa_sdk.knowledge_base.actions import ActionQueryKnowledgeBase

class MyKnowledgeBaseAction(ActionQueryKnowledgeBase):
    def __init__(self):
        knowledge_base = InMemoryKnowledgeBase("maori_knowledge_base.json")
        super().__init__(knowledge_base)

    def name(self) -> Text:
        return "action_query_knowledge_base"

    def utter_attribute_value(self,
                              dispatcher: CollectingDispatcher,
                              object_name = Text,
                              attribute_name = Text,
                              attribute_value = Text):
        """
        The action for a direct query for a specific attribute's value for a specific
        knowledge base entry.
        Args:
            dispatcher: the dispatcher
            object_name: the queried object name
            attribute_name: the queried attribute name
            attribute_value: the value for attribute 'attribute_name' of queried entry
        """
        if attribute_value:
            if attribute_name == 'english':
                dispatcher.utter_message(
                    text=f"The English word for {object_name} is {attribute_value}."
                )
            elif attribute_name == 'definition':
                dispatcher.utter_message(
                    text=f"A {object_name} is {attribute_value}."
                )
            else:
                dispatcher.utter_message(
                    text=f"{object_name} has the value {attribute_value} for attribute {attribute_name}."
                )
        else:
            dispatcher.utter_message(
                text=f"Did not find a valid value for attribute '{attribute_name}' for object '{object_name}'."
            )

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: "DomainDict",
    ) -> List[Dict[Text, Any]]:
        """
        Executes this action. If the user asks a question about an attribute,
        the knowledge base is queried for that attribute. If the user asks for
        the English translation of a Maori word, a list of object fitting the
        attribute criterion is returned.
        Args:
            dispatcher: the dispatcher
            tracker: the tracker
            domain: the domain
        Returns: list of slots
        """
        object_type = tracker.get_slot(SLOT_OBJECT_TYPE)
        attribute = tracker.get_slot(SLOT_ATTRIBUTE)

        new_request = object_type

        if not object_type:
            # object type always needs to be set as this is needed to query the
            # knowledge base
            dispatcher.utter_message(template="utter_ask_rephrase")
            return []

        if not attribute:
            return await self._query_objects(dispatcher, object_type, tracker)
        elif attribute:
            return await self._query_attribute(
                dispatcher, object_type, attribute, tracker
            )

        dispatcher.utter_message(template="utter_ask_rephrase")
        return []