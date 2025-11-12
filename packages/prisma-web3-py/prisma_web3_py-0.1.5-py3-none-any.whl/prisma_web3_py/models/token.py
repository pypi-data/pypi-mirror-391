"""
Token model - represents cryptocurrency token information.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from sqlalchemy import (
    BigInteger, Boolean, DateTime, Integer, Numeric, String, Text,
    UniqueConstraint, Index, func, text, and_
)
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship, foreign

from ..base import Base


class Token(Base):
    """
    Token model representing cryptocurrency token information and metadata.

    Corresponds to Prisma model: Token
    Table: Token
    """

    __tablename__ = "Token"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Core token info
    chain: Mapped[str] = mapped_column(String(255), nullable=False)
    token_address: Mapped[str] = mapped_column(String(255), nullable=False)
    symbol: Mapped[Optional[str]] = mapped_column(String(255))
    name: Mapped[Optional[str]] = mapped_column(String(255))
    logo: Mapped[Optional[str]] = mapped_column(Text)
    decimals: Mapped[Optional[int]] = mapped_column(Integer)
    total_supply: Mapped[Optional[Decimal]] = mapped_column(Numeric)

    # Social and web links
    website: Mapped[Optional[str]] = mapped_column(Text)
    telegram: Mapped[Optional[str]] = mapped_column(Text)
    twitter: Mapped[Optional[str]] = mapped_column(String(255))

    # Timestamps
    pool_creation_timestamp: Mapped[Optional[int]] = mapped_column(BigInteger)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        onupdate=func.now()
    )
    deploy_time: Mapped[Optional[int]] = mapped_column(BigInteger)
    signal_updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    last_verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Token properties
    can_mint: Mapped[Optional[bool]] = mapped_column(Boolean)
    top_pools: Mapped[Optional[str]] = mapped_column(Text)
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Holder and trader metrics
    rat_trader_amount_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric)
    bluechip_owner_count: Mapped[Optional[int]] = mapped_column(Integer)
    bluechip_owner_percentage: Mapped[Optional[float]] = mapped_column(Numeric)
    degen_call_count: Mapped[Optional[int]] = mapped_column(Integer)
    honeypot: Mapped[Optional[int]] = mapped_column(Integer)
    signal_count: Mapped[Optional[int]] = mapped_column(Integer)
    top_10_holder_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric)
    top_fresh_wallet_count: Mapped[Optional[int]] = mapped_column(Integer)
    top_rat_trader_amount_percentage: Mapped[Optional[float]] = mapped_column(Numeric)
    top_rat_trader_count: Mapped[Optional[int]] = mapped_column(Integer)
    top_smart_degen_count: Mapped[Optional[int]] = mapped_column(Integer)
    top_trader_fresh_wallet_count: Mapped[Optional[int]] = mapped_column(Integer)
    top_trader_rat_trader_amount_percentage: Mapped[Optional[float]] = mapped_column(Numeric)
    top_trader_rat_trader_count: Mapped[Optional[int]] = mapped_column(Integer)
    top_trader_smart_degen_count: Mapped[Optional[int]] = mapped_column(Integer)

    # Scoring
    score: Mapped[Optional[Decimal]] = mapped_column(Numeric)
    signal_score: Mapped[Optional[Decimal]] = mapped_column(Numeric)
    metrics_score: Mapped[Optional[Decimal]] = mapped_column(Numeric)
    top_buys_score: Mapped[Optional[Decimal]] = mapped_column(Numeric)

    # Additional metadata
    raw_metadata: Mapped[Optional[dict]] = mapped_column(JSON)
    creator_address: Mapped[Optional[str]] = mapped_column(String(255))
    aliases: Mapped[Optional[list]] = mapped_column(
        JSON,
        server_default=text("'[]'::json")
    )
    categories: Mapped[Optional[list]] = mapped_column(
        JSON,
        server_default=text("'[]'::json")
    )

    # Verification
    is_mainnet: Mapped[Optional[bool]] = mapped_column(
        Boolean,
        server_default=text("false")
    )
    coingecko_id: Mapped[Optional[str]] = mapped_column(String(255))
    verification_status: Mapped[Optional[str]] = mapped_column(
        String(50),
        server_default=text("'pending'::character varying")
    )

    # Relationships (lazy loading for async)
    signals: Mapped[List["Signal"]] = relationship(
        "Signal",
        back_populates="token",
        lazy="selectin",
        viewonly=True
    )
    pre_signals: Mapped[List["PreSignal"]] = relationship(
        "PreSignal",
        back_populates="token",
        lazy="selectin",
        viewonly=True
    )
    token_metrics: Mapped[Optional["TokenMetrics"]] = relationship(
        "TokenMetrics",
        back_populates="token",
        uselist=False,
        lazy="selectin",
        viewonly=True
    )
    token_analysis_reports: Mapped[List["TokenAnalysisReport"]] = relationship(
        "TokenAnalysisReport",
        back_populates="token",
        lazy="selectin",
        viewonly=True
    )

    # Table constraints
    __table_args__ = (
        UniqueConstraint('chain', 'token_address', name='Token_chain_token_address_key'),
        Index('Token_chain_idx', 'chain'),
        Index('Token_token_address_idx', 'token_address'),
        Index('idx_token_chain_address_optimized', 'chain', 'token_address', 'symbol', 'name'),
        Index('idx_token_aliases_gin', 'aliases', postgresql_using='gin'),
        Index('idx_token_coingecko_id', 'coingecko_id'),
        Index('idx_token_verification', 'verification_status', 'last_verified_at'),
        {'schema': 'public'}
    )

    def __repr__(self):
        return f"<Token(id={self.id}, symbol={self.symbol}, chain={self.chain}, address={self.token_address})>"

    def to_dict(self) -> dict:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "chain": self.chain,
            "token_address": self.token_address,
            "symbol": self.symbol,
            "name": self.name,
            "logo": self.logo,
            "decimals": self.decimals,
            "total_supply": str(self.total_supply) if self.total_supply else None,
            "website": self.website,
            "telegram": self.telegram,
            "twitter": self.twitter,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "verification_status": self.verification_status,
            "score": str(self.score) if self.score else None,
        }
