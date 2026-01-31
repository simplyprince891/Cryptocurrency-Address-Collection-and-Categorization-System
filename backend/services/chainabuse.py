"""
Chainabuse API Integration Service

Provides access to Chainabuse threat intelligence database.
Uses permanent database caching to minimize API calls.
"""

import os
import json
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


@dataclass
class ChainabuseReport:
    """Single abuse report from Chainabuse"""
    report_id: str
    category: str
    subcategory: Optional[str]
    description: str
    amount_lost: Optional[float]
    currency: str
    confidence: float
    reported_date: Optional[str]


@dataclass
class ChainabuseReportSummary:
    """Summary of all reports for an address"""
    address: str
    report_count: int
    reports: List[ChainabuseReport]
    total_amount_lost: float
    highest_confidence: float
    categories: List[str]
    risk_level: str  # 'NONE', 'LOW', 'MEDIUM', 'HIGH'


class ChainabuseClient:
    """Client for Chainabuse API with permanent database caching"""
    
    BASE_URL = "https://www.chainabuse.com/api"
    
    def __init__(self, api_key: Optional[str] = None, db_session=None):
        """
        Initialize Chainabuse client
        
        Args:
            api_key: Chainabuse API key (or loads from CHAINABUSE_API_KEY env var)
            db_session: SQLAlchemy database session for caching
        """
        self.api_key = api_key or os.getenv('CHAINABUSE_API_KEY')
        self.db = db_session
        
        # Setup HTTP session
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        if self.api_key:
            self.session.headers.update({
                'Authorization': f'Bearer {self.api_key}'
            })
    
    def is_configured(self) -> bool:
        """Check if API key is configured"""
        return self.api_key is not None
    
    def get_address_reports(self, address: str, force_refresh: bool = False) -> Optional[ChainabuseReportSummary]:
        """
        Get abuse reports for an address (with permanent caching)
        
        Args:
            address: Cryptocurrency address to check
            force_refresh: Force API call even if cached data exists
            
        Returns:
            ChainabuseReportSummary or None if API unavailable/failed
        """
        if not self.is_configured():
            print("[INFO] Chainabuse API not configured, skipping check")
            return None
        
        # Check permanent database cache first
        if not force_refresh and self.db:
            from models import ChainabuseCache
            cached = ChainabuseCache.query.get(address)
            if cached:
                print(f"[INFO] Using permanently cached Chainabuse data for {address} (cached: {cached.cached_at})")
                return self._cached_to_summary(cached)
        
        try:
            # Call Chainabuse screening endpoint
            # Note: Adjust endpoint based on actual Chainabuse API documentation
            response = self.session.get(
                f"{self.BASE_URL}/screening/{address}",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # DEBUG: Show what Chainabuse actually returned
                print(f"[DEBUG] Chainabuse API response keys: {list(data.keys())}")
                print(f"[DEBUG] Chainabuse full response: {data}")
                
                summary = self._parse_response(address, data)
                
                # Save to permanent cache
                if self.db:
                    self._save_to_cache(address, summary)
                
                return summary
            
            elif response.status_code == 404:
                # No reports found (clean address)
                summary = ChainabuseReportSummary(
                    address=address,
                    report_count=0,
                    reports=[],
                    total_amount_lost=0.0,
                    highest_confidence=0.0,
                    categories=[],
                    risk_level='NONE'
                )
                
                # Cache "no reports" result permanently
                if self.db:
                    self._save_to_cache(address, summary)
                
                return summary
            
            elif response.status_code == 429:
                print("[WARNING] Chainabuse rate limit exceeded")
                return None
            
            else:
                print(f"[WARNING] Chainabuse API error: {response.status_code}")
                return None
        
        except requests.exceptions.Timeout:
            print("[WARNING] Chainabuse API timeout")
            return None
        
        except Exception as e:
            print(f"[ERROR] Chainabuse API call failed: {str(e)}")
            return None
    
    def _cached_to_summary(self, cached) -> ChainabuseReportSummary:
        """Convert database cache object to summary"""
        cached_data = cached.to_dict()
        
        # Reconstruct report objects
        reports = []
        for r in cached_data.get('reports', []):
            report = ChainabuseReport(
                report_id=r.get('report_id', 'unknown'),
                category=r.get('category', 'Unknown'),
                subcategory=r.get('subcategory'),
                description=r.get('description', ''),
                amount_lost=r.get('amount_lost', 0),
                currency=r.get('currency', 'USD'),
                confidence=r.get('confidence', 0.5),
                reported_date=r.get('reported_date')
            )
            reports.append(report)
        
        # LOG: Show cached data stats
        print(f"[INFO] Chainabuse (cached): Found {cached.report_count} reports for {cached.address[:20]}...")
        if cached.report_count > 0:
            print(f"[INFO] Chainabuse (cached): Categories={cached_data.get('categories', [])}")
        
        return ChainabuseReportSummary(
            address=cached.address,
            report_count=cached.report_count,
            reports=reports,
            total_amount_lost=cached.total_amount_lost,
            highest_confidence=cached.highest_confidence,
            categories=cached_data.get('categories', []),
            risk_level=self._determine_risk_level(cached.report_count, cached.highest_confidence)
        )
    
    def _save_to_cache(self, address: str, summary: ChainabuseReportSummary):
        """Save Chainabuse response to permanent database cache"""
        from models import ChainabuseCache, db
        
        try:
            # Serialize reports to JSON
            reports_json = json.dumps([{
                'report_id': r.report_id,
                'category': r.category,
                'subcategory': r.subcategory,
                'description': r.description,
                'amount_lost': r.amount_lost,
                'currency': r.currency,
                'confidence': r.confidence,
                'reported_date': r.reported_date
            } for r in summary.reports])
            
            categories_json = json.dumps(summary.categories)
            
            # Check if already exists
            existing = ChainabuseCache.query.get(address)
            if existing:
                # Update existing
                existing.report_count = summary.report_count
                existing.categories = categories_json
                existing.reports_data = reports_json
                existing.highest_confidence = summary.highest_confidence
                existing.total_amount_lost = summary.total_amount_lost
                existing.cached_at = datetime.utcnow()
            else:
                # Create new
                cache_entry = ChainabuseCache(
                    address=address,
                    report_count=summary.report_count,
                    categories=categories_json,
                    reports_data=reports_json,
                    highest_confidence=summary.highest_confidence,
                    total_amount_lost=summary.total_amount_lost
                )
                db.session.add(cache_entry)
            
            db.session.commit()
            print(f"[INFO] Saved Chainabuse data to permanent cache for {address}")
        
        except Exception as e:
            print(f"[ERROR] Failed to save to cache: {str(e)}")
            db.session.rollback()
    
    def _determine_risk_level(self, report_count: int, confidence: float) -> str:
        """Determine risk level from report count and confidence"""
        if report_count == 0:
            return 'NONE'
        elif report_count >= 5 or confidence > 0.8:
            return 'HIGH'
        elif report_count >= 2 or confidence > 0.5:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _parse_response(self, address: str, data: dict) -> ChainabuseReportSummary:
        """
        Parse Chainabuse API response
        
        Note: This is a placeholder implementation.
        Actual parsing depends on Chainabuse API response format.
        """
        reports = []
        categories_set = set()
        total_amount = 0.0
        max_confidence = 0.0
        
        # Parse reports (adjust based on actual API structure)
        report_data = data.get('reports', [])
        
        for r in report_data:
            category = r.get('abuse_type', 'Unknown')
            categories_set.add(category)
            
            amount = float(r.get('amount', 0) or 0)
            total_amount += amount
            
            confidence = float(r.get('confidence', 0.5))
            max_confidence = max(max_confidence, confidence)
            
            report = ChainabuseReport(
                report_id=r.get('id', 'unknown'),
                category=category,
                subcategory=r.get('subcategory'),
                description=r.get('description', '')[:200],  # Truncate
                amount_lost=amount,
                currency=r.get('currency', 'USD'),
                confidence=confidence,
                reported_date=r.get('created_at')
            )
            reports.append(report)
        
        # Determine risk level
        report_count = len(reports)
        if report_count == 0:
            risk_level = 'NONE'
        elif report_count >= 5 or max_confidence > 0.8:
            risk_level = 'HIGH'
        elif report_count >= 2 or max_confidence > 0.5:
            risk_level = 'MEDIUM'
        else:
            risk_level = 'LOW'
        
        # LOG: Show what was found
        print(f"[INFO] Chainabuse: Found {report_count} reports for {address[:20]}...")
        if report_count > 0:
            print(f"[INFO] Chainabuse: Risk={risk_level}, Max confidence={max_confidence:.2f}, Total lost=${total_amount:.2f}")
        
        return ChainabuseReportSummary(
            address=address,
            report_count=report_count,
            reports=reports,
            total_amount_lost=total_amount,
            highest_confidence=max_confidence,
            categories=list(categories_set),
            risk_level=risk_level
        )


# Singleton instance
_client_instance = None


def get_chainabuse_client() -> ChainabuseClient:
    """Get singleton Chainabuse client instance"""
    global _client_instance
    if _client_instance is None:
        _client_instance = ChainabuseClient()
    return _client_instance
