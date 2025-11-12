"""
Message type definitions for the Antonnia SDK.
"""

from datetime import datetime
from pydantic import BaseModel
from typing import Any, Dict, Literal, Optional, Union

# Message role types
MessageRole = Literal["user", "assistant"]

# Message delivery status types
MessageDeliveryStatus = Literal["pending", "sent", "delivered", "read", "failed", "rejected"]


class MessageContentText(BaseModel):
    """Text message content."""
    type: Literal["text"]
    text: str
    template_id: Optional[str] = None
    template_parameters: Optional[Dict[str, Any]] = None

class MessageContentImage(BaseModel):
    """Image message content."""
    type: Literal["image"]
    url: str


class MessageContentAudio(BaseModel):
    """Audio message content."""
    type: Literal["audio"]
    url: str
    transcript: Optional[str] = None


class MessageContentFile(BaseModel):
    """File message content."""
    type: Literal["file"]
    url: str
    mime_type: str
    name: str


class MessageContentFunctionCall(BaseModel):
    """Function call message content."""
    type: Literal["function_call"]
    id: str
    name: str
    input: str


class MessageContentFunctionResult(BaseModel):
    """Function result message content."""
    type: Literal["function_result"]
    id: str
    name: str
    output: str


class MessageContentThought(BaseModel):
    """Thought message content (internal AI reasoning)."""
    type: Literal["thought"]
    thought: str


# Union type for all message content types
MessageContent = Union[
    MessageContentText,
    MessageContentImage,
    MessageContentAudio,
    MessageContentFile,
    MessageContentFunctionCall,
    MessageContentFunctionResult,
    MessageContentThought,
]


class Message(BaseModel):
    """
    Represents a message within a conversation session.
    
    Messages can contain different types of content (text, images, audio, etc.)
    and are associated with a specific role (user or assistant).
    """
    
    id: str
    session_id: str
    conversation_id: str
    organization_id: str
    provider_message_id: Optional[str] = None
    replied_provider_message_id: Optional[str] = None
    role: MessageRole
    content: MessageContent
    created_at: datetime
    delivery_status: Optional[MessageDeliveryStatus] = "pending"
    delivery_error_code: Optional[int] = None
    delivery_error_message: Optional[str] = None
    delivered_at: Optional[datetime] = None
    
    class Config:
        """Pydantic model configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        } 



MESSAGE_ERROR_CODES = {
    131000: "Ocorreu um erro. A mensagem falhou devido a um erro desconhecido.",
    131026: "Mensagem não entregue. O destinatário é incapaz de receber esta mensagem.",
    131042: "Problema de elegibilidade ou pagamento comercial. A mensagem falhou devido ao método de pagamento ou à elegibilidade da conta do WABA.",
    131045: "Erro de certificado ou registro de número de telefone incorreto. A mensagem falhou devido ao registro do número de telefone.",
    131047: "Mensagem de reengajamento. A janela de 24 horas expirou; é necessário usar uma mensagem de modelo (template).",
    131048: "Limite de taxa de spam atingido. Há restrições sobre quantas mensagens podem ser enviadas a partir deste número.",
    131049: "Meta optou por não entregar. Mensagem não entregue para manter um engajamento saudável no ecossistema.",
    131050: "Usuário interrompeu o recebimento de mensagens de marketing. Mensagens de modelo de marketing foram bloqueadas para este usuário.",
    131051: "Tipo de mensagem não suportado. O tipo de mensagem não é compatível.",
    131052: "Erro no download de mídia. Não foi possível baixar a mídia enviada pelo usuário.",
    131053: "Erro no upload de mídia. Não foi possível enviar a mídia usada na mensagem.",
    130429: "Limite de taxa atingido. O limite de taxa de envio de mensagens da Cloud API foi alcançado.",
    131056: "Limite de taxa entre empresa e consumidor atingido. Muitas mensagens enviadas deste remetente para este destinatário.",
    131057: "Conta em modo de manutenção. A conta comercial do WhatsApp está temporariamente indisponível.",
    130472: "Mensagem não enviada: o número do destinatário faz parte de um experimento.",
}


