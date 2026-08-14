# Engineering Rules

MeterSpec uses hard filters before scoring products.

- Maximum current must be positive.
- CT sizing selects the smallest configured standard primary rating that is not below maximum expected current.
- Existing CTs are flagged when the primary rating is below expected maximum current or the secondary output does not match the requirement.
- Nominal voltage must fall inside the fictional meter input range.
- Wiring, CT input, protocol, mounting, and requested measurements must be supported by the product.
- PT requirement is based on the selected fictional catalog voltage input limit and customer preference.
- The tool returns `ENGINEERING REVIEW REQUIRED` when the sample catalog cannot satisfy the requirement.
