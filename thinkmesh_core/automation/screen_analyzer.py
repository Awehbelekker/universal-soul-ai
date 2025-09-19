"""
Advanced Screen Analysis System
==============================

Comprehensive screen analysis using computer vision, OCR, and AI
for intelligent interface understanding and automation planning.
"""

import cv2
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
import logging
from PIL import Image
from dataclasses import dataclass
import time

from ..logging import get_logger
from ..exceptions import ThinkMeshException, ErrorCode

logger = get_logger(__name__)


@dataclass
class ScreenElement:
    """Represents a detected screen element"""
    element_id: str
    element_type: str
    coordinates: Tuple[int, int, int, int]  # x, y, width, height
    center_point: Tuple[int, int]
    text_content: Optional[str] = None
    confidence: float = 0.0
    interactive: bool = False
    attributes: Dict[str, Any] = None


@dataclass
class ScreenAnalysisResult:
    """Complete screen analysis results"""
    elements: List[ScreenElement]
    text_regions: List[Dict[str, Any]]
    interactive_areas: List[ScreenElement]
    layout_structure: Dict[str, Any]
    confidence_score: float
    analysis_time: float


class ScreenAnalyzer:
    """Advanced screen analysis using multiple computer vision techniques"""
    
    def __init__(self):
        self.ocr_engine = OCREngine()
        self.ui_detector = UIElementDetector()
        self.layout_analyzer = LayoutAnalyzer()
        
    async def analyze_screen(self, screenshot: np.ndarray, 
                           context: Optional[Dict[str, Any]] = None) -> ScreenAnalysisResult:
        """Perform comprehensive screen analysis"""
        start_time = time.time()
        
        try:
            # Detect UI elements
            ui_elements = await self.ui_detector.detect_elements(screenshot)
            
            # Extract text regions
            text_regions = await self.ocr_engine.extract_text_regions(screenshot)
            
            # Identify interactive areas
            interactive_areas = await self._identify_interactive_areas(ui_elements, text_regions)
            
            # Analyze layout structure
            layout_structure = await self.layout_analyzer.analyze_layout(screenshot, ui_elements)
            
            # Convert to ScreenElement objects
            screen_elements = await self._convert_to_screen_elements(ui_elements, text_regions)
            
            # Calculate overall confidence
            confidence_score = self._calculate_confidence(screen_elements, text_regions, interactive_areas)
            
            analysis_time = time.time() - start_time
            
            return ScreenAnalysisResult(
                elements=screen_elements,
                text_regions=text_regions,
                interactive_areas=interactive_areas,
                layout_structure=layout_structure,
                confidence_score=confidence_score,
                analysis_time=analysis_time
            )
            
        except Exception as e:
            logger.error(f"Screen analysis failed: {e}")
            raise ThinkMeshException(
                f"Screen analysis error: {e}",
                ErrorCode.SCREEN_ANALYSIS_FAILED
            )
    
    async def _identify_interactive_areas(self, ui_elements: List[Dict[str, Any]], 
                                        text_regions: List[Dict[str, Any]]) -> List[ScreenElement]:
        """Identify interactive areas from detected elements"""
        interactive_areas = []
        
        for element in ui_elements:
            if self._is_likely_interactive(element):
                screen_element = ScreenElement(
                    element_id=element.get('id', 'unknown'),
                    element_type=element.get('type', 'interactive'),
                    coordinates=(element['x'], element['y'], element['width'], element['height']),
                    center_point=(element.get('center_x', element['x']), element.get('center_y', element['y'])),
                    confidence=element.get('confidence', 0.5),
                    interactive=True,
                    attributes=element
                )
                interactive_areas.append(screen_element)
        
        return interactive_areas
    
    def _is_likely_interactive(self, element: Dict[str, Any]) -> bool:
        """Determine if an element is likely interactive"""
        element_type = element.get('type', '').lower()
        width = element.get('width', 0)
        height = element.get('height', 0)
        area = element.get('area', width * height)
        
        # Interactive element heuristics
        interactive_types = ['button', 'input', 'input_field', 'link', 'checkbox', 'radio']
        
        if element_type in interactive_types:
            return True
        
        # Size-based heuristics
        if 30 < width < 400 and 20 < height < 100 and 600 < area < 40000:
            return True
        
        return False
    
    async def _convert_to_screen_elements(self, ui_elements: List[Dict[str, Any]], 
                                        text_regions: List[Dict[str, Any]]) -> List[ScreenElement]:
        """Convert detected elements to ScreenElement objects"""
        screen_elements = []
        
        for i, element in enumerate(ui_elements):
            # Find associated text
            associated_text = self._find_associated_text(element, text_regions)
            
            screen_element = ScreenElement(
                element_id=element.get('id', f'element_{i}'),
                element_type=element.get('type', 'unknown'),
                coordinates=(element['x'], element['y'], element['width'], element['height']),
                center_point=(element.get('center_x', element['x']), element.get('center_y', element['y'])),
                text_content=associated_text,
                confidence=element.get('confidence', 0.5),
                interactive=self._is_likely_interactive(element),
                attributes=element
            )
            screen_elements.append(screen_element)
        
        return screen_elements
    
    def _find_associated_text(self, element: Dict[str, Any], 
                            text_regions: List[Dict[str, Any]]) -> Optional[str]:
        """Find text associated with a UI element"""
        element_x, element_y = element['x'], element['y']
        element_w, element_h = element['width'], element['height']
        
        for text_region in text_regions:
            text_x, text_y = text_region['x'], text_region['y']
            text_w, text_h = text_region['width'], text_region['height']
            
            # Check if text is within or overlapping the element
            if (element_x <= text_x <= element_x + element_w and 
                element_y <= text_y <= element_y + element_h):
                return text_region['text']
            
            # Check if text is near the element (for labels)
            distance = ((text_x - element_x) ** 2 + (text_y - element_y) ** 2) ** 0.5
            if distance < 50:  # Within 50 pixels
                return text_region['text']
        
        return None
    
    def _calculate_confidence(self, screen_elements: List[ScreenElement], 
                            text_regions: List[Dict[str, Any]], 
                            interactive_areas: List[ScreenElement]) -> float:
        """Calculate overall confidence score for the analysis"""
        
        # Factor in number of elements detected
        element_score = min(1.0, len(screen_elements) / 10.0)
        
        # Factor in text detection quality
        text_score = min(1.0, len(text_regions) / 5.0)
        
        # Factor in interactive element detection
        interactive_score = min(1.0, len(interactive_areas) / 3.0)
        
        # Factor in average element confidence
        if screen_elements:
            avg_confidence = sum(elem.confidence for elem in screen_elements) / len(screen_elements)
        else:
            avg_confidence = 0.5
        
        # Weighted combination
        overall_confidence = (
            element_score * 0.3 +
            text_score * 0.2 +
            interactive_score * 0.3 +
            avg_confidence * 0.2
        )
        
        return max(0.1, min(1.0, overall_confidence))


class OCREngine:
    """Optical Character Recognition engine for text extraction"""
    
    def __init__(self):
        self.tesseract_available = self._check_tesseract_availability()
        self.easyocr_available = self._check_easyocr_availability()
        
    def _check_tesseract_availability(self) -> bool:
        """Check if Tesseract OCR is available"""
        try:
            import pytesseract
            return True
        except ImportError:
            logger.warning("pytesseract not available")
            return False
    
    def _check_easyocr_availability(self) -> bool:
        """Check if EasyOCR is available"""
        try:
            import easyocr
            return True
        except ImportError:
            logger.warning("easyocr not available")
            return False
    
    async def extract_text_regions(self, screenshot: np.ndarray) -> List[Dict[str, Any]]:
        """Extract text regions from screenshot"""
        
        if self.easyocr_available:
            return await self._extract_with_easyocr(screenshot)
        elif self.tesseract_available:
            return await self._extract_with_tesseract(screenshot)
        else:
            logger.warning("No OCR engine available")
            return []
    
    async def _extract_with_easyocr(self, screenshot: np.ndarray) -> List[Dict[str, Any]]:
        """Extract text using EasyOCR"""
        try:
            import easyocr
            
            # Initialize EasyOCR reader
            reader = easyocr.Reader(['en'])
            
            # Extract text with bounding boxes
            results = reader.readtext(screenshot)
            
            text_regions = []
            for i, (bbox, text, confidence) in enumerate(results):
                # Convert bbox to x, y, width, height
                x_coords = [point[0] for point in bbox]
                y_coords = [point[1] for point in bbox]
                
                x = int(min(x_coords))
                y = int(min(y_coords))
                width = int(max(x_coords) - min(x_coords))
                height = int(max(y_coords) - min(y_coords))
                
                text_regions.append({
                    'id': f'text_{i}',
                    'text': text,
                    'x': x,
                    'y': y,
                    'width': width,
                    'height': height,
                    'confidence': confidence,
                    'method': 'easyocr'
                })
            
            return text_regions
            
        except Exception as e:
            logger.error(f"EasyOCR extraction failed: {e}")
            return []
    
    async def _extract_with_tesseract(self, screenshot: np.ndarray) -> List[Dict[str, Any]]:
        """Extract text using Tesseract OCR"""
        try:
            import pytesseract
            
            # Convert to PIL Image
            pil_image = Image.fromarray(cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB))
            
            # Extract text with bounding boxes
            data = pytesseract.image_to_data(pil_image, output_type=pytesseract.Output.DICT)
            
            text_regions = []
            for i in range(len(data['text'])):
                text = data['text'][i].strip()
                if text and len(text) > 1:
                    text_regions.append({
                        'id': f'text_{i}',
                        'text': text,
                        'x': data['left'][i],
                        'y': data['top'][i],
                        'width': data['width'][i],
                        'height': data['height'][i],
                        'confidence': data['conf'][i] / 100.0,
                        'method': 'tesseract'
                    })
            
            return text_regions
            
        except Exception as e:
            logger.error(f"Tesseract extraction failed: {e}")
            return []


class UIElementDetector:
    """Detects UI elements using computer vision techniques"""
    
    def __init__(self):
        self.detection_methods = ['contour', 'template', 'edge']
        
    async def detect_elements(self, screenshot: np.ndarray) -> List[Dict[str, Any]]:
        """Detect UI elements using multiple methods"""
        
        all_elements = []
        
        # Method 1: Contour-based detection
        contour_elements = await self._detect_with_contours(screenshot)
        all_elements.extend(contour_elements)
        
        # Method 2: Edge-based detection
        edge_elements = await self._detect_with_edges(screenshot)
        all_elements.extend(edge_elements)
        
        # Method 3: Template matching (for common UI elements)
        template_elements = await self._detect_with_templates(screenshot)
        all_elements.extend(template_elements)
        
        # Remove duplicates and merge overlapping elements
        merged_elements = await self._merge_overlapping_elements(all_elements)
        
        return merged_elements
    
    async def _detect_with_contours(self, screenshot: np.ndarray) -> List[Dict[str, Any]]:
        """Detect elements using contour analysis"""
        elements = []
        
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
            
            # Apply Gaussian blur to reduce noise
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Apply threshold
            _, binary = cv2.threshold(blurred, 127, 255, cv2.THRESH_BINARY)
            
            # Find contours
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for i, contour in enumerate(contours):
                # Get bounding rectangle
                x, y, w, h = cv2.boundingRect(contour)
                
                # Filter based on size
                if w > 15 and h > 15 and w < screenshot.shape[1] * 0.8 and h < screenshot.shape[0] * 0.8:
                    area = cv2.contourArea(contour)
                    perimeter = cv2.arcLength(contour, True)
                    
                    # Calculate shape features
                    aspect_ratio = w / h if h > 0 else 1
                    extent = area / (w * h) if w * h > 0 else 0
                    solidity = area / cv2.contourArea(cv2.convexHull(contour)) if cv2.contourArea(cv2.convexHull(contour)) > 0 else 0
                    
                    element_type = self._classify_by_shape(w, h, aspect_ratio, extent, solidity)
                    
                    elements.append({
                        'id': f'contour_{i}',
                        'type': element_type,
                        'x': x,
                        'y': y,
                        'width': w,
                        'height': h,
                        'center_x': x + w // 2,
                        'center_y': y + h // 2,
                        'area': int(area),
                        'perimeter': int(perimeter),
                        'aspect_ratio': aspect_ratio,
                        'extent': extent,
                        'solidity': solidity,
                        'confidence': 0.6,
                        'detection_method': 'contour'
                    })
                    
        except Exception as e:
            logger.error(f"Contour detection failed: {e}")
        
        return elements
    
    async def _detect_with_edges(self, screenshot: np.ndarray) -> List[Dict[str, Any]]:
        """Detect elements using edge detection"""
        elements = []
        
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
            
            # Apply Canny edge detection
            edges = cv2.Canny(gray, 50, 150, apertureSize=3)
            
            # Find lines using Hough transform
            lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, minLineLength=50, maxLineGap=10)
            
            if lines is not None:
                # Group lines into rectangular regions
                rectangles = self._group_lines_to_rectangles(lines)
                
                for i, rect in enumerate(rectangles):
                    x, y, w, h = rect
                    
                    elements.append({
                        'id': f'edge_{i}',
                        'type': 'rectangle',
                        'x': x,
                        'y': y,
                        'width': w,
                        'height': h,
                        'center_x': x + w // 2,
                        'center_y': y + h // 2,
                        'area': w * h,
                        'confidence': 0.5,
                        'detection_method': 'edge'
                    })
                    
        except Exception as e:
            logger.error(f"Edge detection failed: {e}")
        
        return elements
    
    async def _detect_with_templates(self, screenshot: np.ndarray) -> List[Dict[str, Any]]:
        """Detect elements using template matching"""
        # This would involve matching against common UI element templates
        # For now, return empty list as templates would need to be pre-defined
        return []
    
    def _classify_by_shape(self, width: int, height: int, aspect_ratio: float, 
                          extent: float, solidity: float) -> str:
        """Classify element type based on shape characteristics"""
        
        area = width * height
        
        # Button detection
        if (0.5 <= aspect_ratio <= 3.0 and 
            1000 < area < 20000 and 
            extent > 0.7 and 
            solidity > 0.8):
            return 'button'
        
        # Input field detection
        elif (aspect_ratio > 2.0 and 
              height < 60 and 
              width > 100 and 
              extent > 0.8):
            return 'input_field'
        
        # Text label detection
        elif (aspect_ratio > 3.0 and 
              height < 40 and 
              extent > 0.6):
            return 'text_label'
        
        # Container detection
        elif (area > 50000 and 
              extent > 0.5):
            return 'container'
        
        # Icon detection
        elif (0.8 <= aspect_ratio <= 1.2 and 
              area < 2000 and 
              solidity > 0.7):
            return 'icon'
        
        else:
            return 'unknown'
    
    def _group_lines_to_rectangles(self, lines) -> List[Tuple[int, int, int, int]]:
        """Group detected lines into rectangular regions"""
        # Simplified implementation - in practice this would be more sophisticated
        rectangles = []
        
        # This is a placeholder - actual implementation would analyze line orientations
        # and group horizontal/vertical lines to form rectangles
        
        return rectangles
    
    async def _merge_overlapping_elements(self, elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Merge overlapping elements to reduce duplicates"""
        if not elements:
            return elements
        
        merged = []
        used_indices = set()
        
        for i, elem1 in enumerate(elements):
            if i in used_indices:
                continue
                
            # Find overlapping elements
            overlapping = [elem1]
            used_indices.add(i)
            
            for j, elem2 in enumerate(elements[i+1:], i+1):
                if j in used_indices:
                    continue
                    
                if self._elements_overlap(elem1, elem2):
                    overlapping.append(elem2)
                    used_indices.add(j)
            
            # Merge overlapping elements
            if len(overlapping) > 1:
                merged_element = self._merge_elements(overlapping)
                merged.append(merged_element)
            else:
                merged.append(elem1)
        
        return merged
    
    def _elements_overlap(self, elem1: Dict[str, Any], elem2: Dict[str, Any]) -> bool:
        """Check if two elements overlap significantly"""
        x1, y1, w1, h1 = elem1['x'], elem1['y'], elem1['width'], elem1['height']
        x2, y2, w2, h2 = elem2['x'], elem2['y'], elem2['width'], elem2['height']
        
        # Calculate overlap area
        overlap_x = max(0, min(x1 + w1, x2 + w2) - max(x1, x2))
        overlap_y = max(0, min(y1 + h1, y2 + h2) - max(y1, y2))
        overlap_area = overlap_x * overlap_y
        
        # Calculate union area
        area1 = w1 * h1
        area2 = w2 * h2
        union_area = area1 + area2 - overlap_area
        
        # Check if overlap is significant (IoU > 0.3)
        iou = overlap_area / union_area if union_area > 0 else 0
        return iou > 0.3
    
    def _merge_elements(self, elements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Merge multiple overlapping elements into one"""
        if not elements:
            return {}
        
        # Find bounding box of all elements
        min_x = min(elem['x'] for elem in elements)
        min_y = min(elem['y'] for elem in elements)
        max_x = max(elem['x'] + elem['width'] for elem in elements)
        max_y = max(elem['y'] + elem['height'] for elem in elements)
        
        width = max_x - min_x
        height = max_y - min_y
        
        # Use properties from the largest element
        largest_elem = max(elements, key=lambda e: e['width'] * e['height'])
        
        merged = largest_elem.copy()
        merged.update({
            'x': min_x,
            'y': min_y,
            'width': width,
            'height': height,
            'center_x': min_x + width // 2,
            'center_y': min_y + height // 2,
            'area': width * height,
            'confidence': sum(elem['confidence'] for elem in elements) / len(elements),
            'merged_from': len(elements)
        })
        
        return merged


class LayoutAnalyzer:
    """Analyzes screen layout structure"""
    
    async def analyze_layout(self, screenshot: np.ndarray, 
                           elements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze the layout structure of the screen"""
        
        layout_info = {
            'screen_dimensions': {
                'width': screenshot.shape[1],
                'height': screenshot.shape[0]
            },
            'element_count': len(elements),
            'layout_type': self._determine_layout_type(elements),
            'regions': self._identify_layout_regions(elements, screenshot.shape),
            'navigation_structure': self._analyze_navigation_structure(elements)
        }
        
        return layout_info
    
    def _determine_layout_type(self, elements: List[Dict[str, Any]]) -> str:
        """Determine the type of layout (grid, list, form, etc.)"""
        
        if not elements:
            return 'empty'
        
        # Analyze element positions to determine layout pattern
        y_positions = [elem['y'] for elem in elements]
        x_positions = [elem['x'] for elem in elements]
        
        # Check for grid pattern
        unique_y = len(set(y_positions))
        unique_x = len(set(x_positions))
        
        if unique_y > 3 and unique_x > 3:
            return 'grid'
        elif unique_y > unique_x:
            return 'vertical_list'
        elif unique_x > unique_y:
            return 'horizontal_list'
        else:
            return 'form'
    
    def _identify_layout_regions(self, elements: List[Dict[str, Any]], 
                               screen_shape: Tuple[int, int, int]) -> Dict[str, Any]:
        """Identify different regions of the layout"""
        
        screen_height, screen_width = screen_shape[:2]
        
        # Define regions
        header_region = []
        content_region = []
        footer_region = []
        sidebar_region = []
        
        for elem in elements:
            y = elem['y']
            x = elem['x']
            
            # Header region (top 20% of screen)
            if y < screen_height * 0.2:
                header_region.append(elem)
            # Footer region (bottom 20% of screen)
            elif y > screen_height * 0.8:
                footer_region.append(elem)
            # Sidebar region (left or right 20% of screen)
            elif x < screen_width * 0.2 or x > screen_width * 0.8:
                sidebar_region.append(elem)
            # Content region (middle area)
            else:
                content_region.append(elem)
        
        return {
            'header': header_region,
            'content': content_region,
            'footer': footer_region,
            'sidebar': sidebar_region
        }
    
    def _analyze_navigation_structure(self, elements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze navigation structure and flow"""
        
        # Identify potential navigation elements
        nav_elements = []
        for elem in elements:
            if elem.get('type') in ['button', 'link'] or 'nav' in elem.get('type', '').lower():
                nav_elements.append(elem)
        
        # Analyze navigation flow
        navigation_info = {
            'navigation_elements': len(nav_elements),
            'primary_navigation': self._find_primary_navigation(nav_elements),
            'secondary_navigation': self._find_secondary_navigation(nav_elements),
            'call_to_action': self._find_call_to_action(nav_elements)
        }
        
        return navigation_info
    
    def _find_primary_navigation(self, nav_elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find primary navigation elements"""
        # Primary navigation is typically at the top or has larger size
        primary_nav = []
        
        for elem in nav_elements:
            if elem['y'] < 200 or elem['area'] > 5000:  # Top area or large elements
                primary_nav.append(elem)
        
        return primary_nav
    
    def _find_secondary_navigation(self, nav_elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find secondary navigation elements"""
        # Secondary navigation is typically smaller or in sidebar
        secondary_nav = []
        
        for elem in nav_elements:
            if elem['area'] < 3000 and elem['y'] > 200:  # Smaller elements not in header
                secondary_nav.append(elem)
        
        return secondary_nav
    
    def _find_call_to_action(self, nav_elements: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Find call-to-action elements"""
        # CTA elements are typically prominent buttons
        cta_elements = []
        
        for elem in nav_elements:
            if (elem.get('type') == 'button' and 
                elem['area'] > 2000 and 
                elem.get('confidence', 0) > 0.7):
                cta_elements.append(elem)
        
        return cta_elements
