---
inclusion: always
---

# Code Style Guidelines

## File Organization

- Combine related functionality in single files
- Keep total file count minimal
- Use clear, descriptive file names

## Code Quality

- Keep functions under 20 lines when possible
- Use type hints for all function signatures
- Prefer simple functions over classes when possible
- No unnecessary abstractions
- DRY principle - extract repeated code immediately

## Python Style

```python
# Good - Simple and clear
def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two coordinates in meters."""
    # Implementation
    return distance

# Bad - Over-engineered
class DistanceCalculator:
    def __init__(self, unit: str = "meters"):
        self.unit = unit
    
    def calculate(self, coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
        # Implementation
        pass
```

## TypeScript/React Style

- Use functional components only
- Keep components under 100 lines
- Extract reusable logic to custom hooks
- Use Tailwind CSS classes directly (no CSS files)

## General Rules

- Write self-documenting code with clear variable names
- Add docstrings only for public functions
- Comment only when logic is non-obvious
- Prefer readability over cleverness
