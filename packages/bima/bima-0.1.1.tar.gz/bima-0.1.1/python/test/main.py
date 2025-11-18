import bima

# Clean Python API - no direct Rust calls
result = bima.compute([1.0, 2.0, 3.0])
print(result)  # 6.0

processor = bima.DataProcessor()
output = processor.process([1.0, 2.0, 3.0])
output
