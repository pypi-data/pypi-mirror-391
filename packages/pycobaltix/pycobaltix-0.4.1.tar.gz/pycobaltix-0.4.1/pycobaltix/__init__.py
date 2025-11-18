"""
pycobaltix - API 응답 형식을 정의하는 유틸리티 패키지
"""

__version__ = "0.2.8"

# 기본 기능: schemas와 slack (기본 dependencies에 포함)
from pycobaltix.schemas.responses import (
    APIResponse,
    ErrorResponse,
    PaginatedAPIResponse,
    PaginationInfo,
)
from pycobaltix.slack import SlackBot, SlackWebHook

__all__ = [
    "APIResponse",
    "PaginatedAPIResponse",
    "PaginationInfo",
    "ErrorResponse",
    "SlackWebHook",
    "SlackBot",
]

# Public 기능 (public optional dependency 필요: 모든 API 관련 의존성)
try:
    # Address 기능
    from pycobaltix.address import (
        convert_coordinate,
        naver_api,
    )

    # V-World API
    from pycobaltix.public import (
        AsyncVWorldAPI,
        BuildingInfo,
        ResponseFormat,
        VWorldAPI,
    )

    # Registration API
    from pycobaltix.public.registration import (
        LandRight,
        OwnershipRecord,
        PropertyType,
        RealEstateInfo,
        RegistrationStatus,
        RegistryDocument,
        RegistryParser,
        RegistryProperty,
        RightRecord,
        search_real_estate,
    )

    __all__.extend(
        [
            # Address 기능
            "convert_coordinate",
            "naver_api",
            # V-World API
            "VWorldAPI",
            "AsyncVWorldAPI",
            "BuildingInfo",
            "ResponseFormat",
            # Registration API
            "search_real_estate",
            "RealEstateInfo",
            "PropertyType",
            "RegistrationStatus",
            "RegistryParser",
            "RegistryDocument",
            "RegistryProperty",
            "LandRight",
            "OwnershipRecord",
            "RightRecord",
        ]
    )
except ImportError:
    pass
