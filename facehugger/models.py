from pydantic import BaseModel
from typing import List, Union, Optional


class ModelConfig(BaseModel):
    """Configuration for a single model in the manifest"""

    repo: str
    ref: Optional[str] = "main"
    include: Optional[Union[str, List[str]]] = None
    exclude: Optional[Union[str, List[str]]] = None


class FacehuggerManifest(BaseModel):
    """Main manifest file structure"""

    models: List[ModelConfig]
