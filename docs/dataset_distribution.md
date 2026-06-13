# Dataset Distribution

## Source

- Dataset config: `dataset/data.yaml`
- Splits: `train`, `val`, `test`
- Classes: `Bus`, `Car`, `Motorcycle`, `Person`, `Truck`, `mini-truck`

## Split-Level Summary

| Split | Images | Label files | Empty labels | Missing labels | Orphan labels | Invalid class ids |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| train | 2770 | 2770 | 0 | 0 | 0 | 0 |
| val | 791 | 791 | 0 | 0 | 0 | 0 |
| test | 396 | 396 | 0 | 0 | 0 | 0 |

## Annotation Count by Class

| Class | train | val | test | total |
| --- | ---: | ---: | ---: | ---: |
| Bus | 843 | 242 | 146 | 1231 |
| Car | 4369 | 1197 | 479 | 6045 |
| Motorcycle | 792 | 249 | 104 | 1145 |
| Person | 4646 | 1332 | 613 | 6591 |
| Truck | 1628 | 409 | 186 | 2223 |
| mini-truck | 1101 | 302 | 114 | 1517 |

## Potential Issues

No empty label, invalid class id, missing label, or orphan label issue was found.

## Notes

- This report only reads dataset files and does not modify the original dataset.
- `val` uses the directory configured in `dataset/data.yaml`: `valid/images`.
- Empty labels are counted when a `.txt` label file exists but contains no annotation lines.
- Invalid class IDs mean the class index is outside the range defined by `names` in `dataset/data.yaml`.
