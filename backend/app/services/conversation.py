import json
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime, timezone
from app.schemas.conversation import Conversation, Message, ImageReference, AnalysisReference

class InMemoryConversationStore:
    def __init__(self):
        self.conversations: Dict[str, Conversation] = {}
        self.messages: Dict[str, List[Message]] = {}
        self.images: Dict[str, List[ImageReference]] = {}
        self.analyses: Dict[str, List[AnalysisReference]] = {}
        self.storage_path = Path(__file__).resolve().parents[2] / "data" / "conversations.json"
        self._load()

    def _load(self) -> None:
        if not self.storage_path.exists():
            return

        try:
            data = json.loads(self.storage_path.read_text(encoding="utf-8"))
            self.conversations = {
                conversation_id: Conversation.model_validate(value)
                for conversation_id, value in data.get("conversations", {}).items()
            }
            self.messages = {
                conversation_id: [Message.model_validate(message) for message in messages]
                for conversation_id, messages in data.get("messages", {}).items()
            }
            self.images = {
                conversation_id: [ImageReference.model_validate(image) for image in images]
                for conversation_id, images in data.get("images", {}).items()
            }
            self.analyses = {
                conversation_id: [AnalysisReference.model_validate(analysis) for analysis in analyses]
                for conversation_id, analyses in data.get("analyses", {}).items()
            }
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            self.conversations = {}
            self.messages = {}
            self.images = {}
            self.analyses = {}

    def _persist(self) -> None:
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "conversations": {
                conversation_id: conversation.model_dump(mode="json")
                for conversation_id, conversation in self.conversations.items()
            },
            "messages": {
                conversation_id: [message.model_dump(mode="json") for message in messages]
                for conversation_id, messages in self.messages.items()
            },
            "images": {
                conversation_id: [image.model_dump(mode="json") for image in images]
                for conversation_id, images in self.images.items()
            },
            "analyses": {
                conversation_id: [analysis.model_dump(mode="json") for analysis in analyses]
                for conversation_id, analyses in self.analyses.items()
            },
        }
        temporary_path = self.storage_path.with_suffix(".tmp")
        temporary_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        temporary_path.replace(self.storage_path)

    def create_conversation(self, context: Optional[Dict[str, Any]] = None) -> Conversation:
        conv = Conversation(context=context)
        self.conversations[conv.conversation_id] = conv
        self.messages[conv.conversation_id] = []
        self.images[conv.conversation_id] = []
        self.analyses[conv.conversation_id] = []
        self._persist()
        return conv

    def add_message(self, conversation_id: str, role: str, text: str) -> Message:
        if conversation_id not in self.conversations:
            raise ValueError("Conversation not found")
            
        msg = Message(conversation_id=conversation_id, role=role, text=text)
        self.messages[conversation_id].append(msg)
        self.conversations[conversation_id].updated_at = datetime.now(timezone.utc)
        self._persist()
        return msg

    def add_image_reference(self, conversation_id: str, filename: str, original_filename: str, metadata: Optional[dict] = None) -> ImageReference:
        if conversation_id not in self.conversations:
            raise ValueError("Conversation not found")
            
        img = ImageReference(
            conversation_id=conversation_id, 
            filename=filename, 
            original_filename=original_filename, 
            metadata=metadata
        )
        self.images[conversation_id].append(img)
        self.conversations[conversation_id].updated_at = datetime.now(timezone.utc)
        self._persist()
        return img

    def add_analysis_result(self, conversation_id: str, task: str, input_image_ids: List[str], result: Any, confidence: Optional[float] = None, evidence: Optional[Any] = None) -> AnalysisReference:
        if conversation_id not in self.conversations:
            raise ValueError("Conversation not found")
            
        analysis = AnalysisReference(
            conversation_id=conversation_id,
            task=task,
            input_image_ids=input_image_ids,
            result=result,
            confidence=confidence,
            evidence=evidence
        )
        self.analyses[conversation_id].append(analysis)
        self.conversations[conversation_id].updated_at = datetime.now(timezone.utc)
        self._persist()
        return analysis

    def get_conversation_history(self, conversation_id: str) -> List[Message]:
        return self.messages.get(conversation_id, [])

    def get_conversation_images(self, conversation_id: str) -> List[ImageReference]:
        return self.images.get(conversation_id, [])

    def get_conversation_analyses(self, conversation_id: str) -> List[AnalysisReference]:
        return self.analyses.get(conversation_id, [])
        
    def get_full_conversation(self, conversation_id: str) -> dict:
        if conversation_id not in self.conversations:
            raise ValueError("Conversation not found")
        return {
            "conversation": self.conversations[conversation_id].model_dump(),
            "messages": [m.model_dump() for m in self.messages[conversation_id]],
            "images": [i.model_dump() for i in self.images[conversation_id]],
            "analyses": [a.model_dump() for a in self.analyses[conversation_id]]
        }

from app.core.database import db

class MongoConversationStore:
    async def create_conversation(self, user_id: str, context: Optional[Dict[str, Any]] = None) -> Conversation:
        conv = Conversation(user_id=user_id, context=context)
        await db.db.conversations.insert_one(conv.model_dump())
        return conv

    async def list_conversations(self, user_id: str) -> List[Dict[str, Any]]:
        cursor = db.db.conversations.find({"user_id": user_id}).sort("updated_at", -1)
        conversations = await cursor.to_list(length=None)
        
        result = []
        for c in conversations:
            conv_id = c.get("conversation_id", "")
            title = f"Conv {conv_id[:6]}" if conv_id else "New Conversation"
            result.append({
                "id": conv_id,
                "title": title,
                "created_at": c.get("created_at"),
                "updated_at": c.get("updated_at")
            })
        return result

    async def add_message(self, user_id: str, conversation_id: str, role: str, text: str) -> Message:
        # Verify ownership
        conv = await db.db.conversations.find_one({"conversation_id": conversation_id, "user_id": user_id})
        if not conv:
            raise ValueError("Conversation not found")
            
        msg = Message(conversation_id=conversation_id, role=role, text=text)
        await db.db.messages.insert_one(msg.model_dump())
        await db.db.conversations.update_one(
            {"conversation_id": conversation_id},
            {"$set": {"updated_at": datetime.now(timezone.utc)}}
        )
        return msg

    async def add_image_reference(self, user_id: str, conversation_id: str, filename: str, original_filename: str, metadata: Optional[dict] = None) -> ImageReference:
        conv = await db.db.conversations.find_one({"conversation_id": conversation_id, "user_id": user_id})
        if not conv:
            raise ValueError("Conversation not found")
            
        img = ImageReference(
            conversation_id=conversation_id, 
            filename=filename, 
            original_filename=original_filename, 
            metadata=metadata
        )
        await db.db.images.insert_one(img.model_dump())
        await db.db.conversations.update_one(
            {"conversation_id": conversation_id},
            {"$set": {"updated_at": datetime.now(timezone.utc)}}
        )
        return img

    async def add_analysis_result(self, user_id: str, conversation_id: str, task: str, input_image_ids: List[str], result: Any, confidence: Optional[float] = None, evidence: Optional[Any] = None) -> AnalysisReference:
        conv = await db.db.conversations.find_one({"conversation_id": conversation_id, "user_id": user_id})
        if not conv:
            raise ValueError("Conversation not found")
            
        analysis = AnalysisReference(
            conversation_id=conversation_id,
            task=task,
            input_image_ids=input_image_ids,
            result=result,
            confidence=confidence,
            evidence=evidence
        )
        await db.db.analyses.insert_one(analysis.model_dump())
        await db.db.conversations.update_one(
            {"conversation_id": conversation_id},
            {"$set": {"updated_at": datetime.now(timezone.utc)}}
        )
        return analysis

    async def get_conversation_images(self, user_id: str, conversation_id: str) -> List[ImageReference]:
        conv = await db.db.conversations.find_one({"conversation_id": conversation_id, "user_id": user_id})
        if not conv:
            raise ValueError("Conversation not found")
        
        cursor = db.db.images.find({"conversation_id": conversation_id}).sort("timestamp", 1)
        images = await cursor.to_list(length=None)
        return [ImageReference.model_validate(img) for img in images]

    async def get_full_conversation(self, user_id: str, conversation_id: str) -> dict:
        conv = await db.db.conversations.find_one({"conversation_id": conversation_id, "user_id": user_id})
        if not conv:
            raise ValueError("Conversation not found")
            
        messages_cursor = db.db.messages.find({"conversation_id": conversation_id}).sort("timestamp", 1)
        messages = await messages_cursor.to_list(length=None)
        
        images_cursor = db.db.images.find({"conversation_id": conversation_id}).sort("timestamp", 1)
        images = await images_cursor.to_list(length=None)
        
        analyses_cursor = db.db.analyses.find({"conversation_id": conversation_id}).sort("timestamp", 1)
        analyses = await analyses_cursor.to_list(length=None)
        
        # Remove MongoDB _id before returning
        conv.pop("_id", None)
        for doc in messages: doc.pop("_id", None)
        for doc in images: doc.pop("_id", None)
        for doc in analyses: doc.pop("_id", None)

        return {
            "conversation": Conversation.model_validate(conv).model_dump(),
            "messages": [Message.model_validate(m).model_dump() for m in messages],
            "images": [ImageReference.model_validate(i).model_dump() for i in images],
            "analyses": [AnalysisReference.model_validate(a).model_dump() for a in analyses]
        }

# Global singleton for in-memory storage (legacy fallback)
legacy_conversation_store = InMemoryConversationStore()

# Global singleton for mongo storage (active)
conversation_store = MongoConversationStore()
