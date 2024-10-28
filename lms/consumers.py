import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Session
from asgiref.sync import sync_to_async

logger = logging.getLogger(__name__)

class SessionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.group_name = f'session_{self.session_id}'
        
        # Logging connection attempt
        logger.info(f"Client attempting to connect to session {self.session_id}")
        
        # Add the client to the session group
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        logger.info(f"Client connected to session {self.session_id}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        logger.info(f"Client disconnected from session {self.session_id}")

    async def receive(self, text_data):
        # Parse the incoming data
        data = json.loads(text_data)
        action = data.get("action")
        logger.info(f"Received action: {action} with data: {data}")
        
        # Handling various actions based on the WebRTC communication or session control
        if action == "start":
            response = await self.start_session()
        elif action == "pause":
            response = await self.pause_session()
        elif action == "stop":
            response = await self.stop_session()
        elif action in ["offer", "answer", "ice_candidate"]:
            response = await self.handle_webrtc_signaling(action, data)
        else:
            response = {"message": "Invalid action", "status": "error"}

        # Send the response back to the client
        await self.send(text_data=json.dumps(response))

    async def start_session(self):
        session = await self.get_session()
        session.is_active = True
        session.is_paused = False
        await self.update_session(session)

        # Log the start of the session
        logger.info(f"Session {self.session_id} started")

        # Broadcast to group that the session has started
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "session_control",
                "message": "Session has started",
                "status": "started",
            }
        )
        return {"message": "Session has started", "status": "started"}

    async def pause_session(self):
        session = await self.get_session()
        session.is_paused = True
        await self.update_session(session)

        # Log the pause of the session
        logger.info(f"Session {self.session_id} paused")

        # Notify group about the pause
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "session_control",
                "message": "Session is paused",
                "status": "paused",
            }
        )
        return {"message": "Session is paused", "status": "paused"}

    async def stop_session(self):
        session = await self.get_session()
        session.is_active = False
        session.is_paused = False
        await self.update_session(session)

        # Log the stop of the session
        logger.info(f"Session {self.session_id} stopped")

        # Notify group that the session has stopped
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "session_control",
                "message": "Session has stopped",
                "status": "stopped",
            }
        )
        return {"message": "Session has stopped", "status": "stopped"}

    async def handle_webrtc_signaling(self, action, data):
        """
        Handle WebRTC signaling actions (offer, answer, ICE candidates)
        and relay them to other clients in the session.
        """
        logger.info(f"Handling WebRTC signaling: {action} with data: {data}")

        # Relay the offer, answer, or ICE candidate to all peers in the group
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "webrtc_signal",
                "action": action,
                **data  # Unpack the offer/answer/candidate data
            }
        )

        return {"message": f"{action} relayed", "status": "success"}

    async def webrtc_signal(self, event):
        """
        Relay WebRTC signaling data to the connected client.
        This handles offer, answer, and ICE candidates.
        """
        logger.info(f"Relaying WebRTC signal: {event}")

        # Send the WebRTC signaling message to the client
        await self.send(text_data=json.dumps({
            "action": event["action"],
            **event  # Send the relayed offer/answer/candidate
        }))

    async def session_control(self, event):
        """
        Send session control updates to the client (e.g., session started, paused, or stopped).
        """
        await self.send(text_data=json.dumps({
            "message": event["message"],
            "status": event["status"],
        }))

    @sync_to_async
    def get_session(self):
        """
        Retrieve the session from the database.
        """
        return Session.objects.get(id=self.session_id)

    @sync_to_async
    def update_session(self, session):
        """
        Save updates to the session in the database.
        """
        session.save()
