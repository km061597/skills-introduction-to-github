# 📊 Example Files

This folder contains sample Excel files to test the converter with different data types and structures.

## Sample Files (To Be Added)

### 1. sample-financial-report.xlsx
**Type:** Financial data with multiple sheets
**Sheets:** Summary, Monthly Data, YTD Comparison
**Rows:** ~100 per sheet
**Columns:** 8-12
**Recommended Settings:**
- Orientation: Portrait
- Fit to Width: Yes
- Headers/Footers: Yes
- Gridlines: Yes

### 2. sample-wide-table.xlsx
**Type:** Wide data table (many columns)
**Sheets:** Inventory Data
**Rows:** ~50
**Columns:** 25
**Recommended Settings:**
- Orientation: Landscape
- Scale: 70%
- Headers/Footers: Yes
- Gridlines: Yes

### 3. sample-dashboard.xlsx
**Type:** Summary dashboard with calculations
**Sheets:** Dashboard, Raw Data
**Rows:** ~30 (dashboard), ~200 (data)
**Columns:** 6 (dashboard), 15 (data)
**Recommended Settings:**
- Orientation: Auto
- Fit to Width: Yes
- Headers/Footers: Yes
- Gridlines: No (cleaner look)

## Creating Your Own Test Files

### Tips for Testing:

1. **Start Simple:** Single sheet with 10 rows, 5 columns
2. **Add Complexity:** Multiple sheets, more columns
3. **Test Edge Cases:**
   - Very wide tables (30+ columns)
   - Very long sheets (1000+ rows)
   - Mixed content (text, numbers, formulas)
   - Empty rows/columns
   - Merged cells

### Test Scenarios:

#### Scenario 1: Standard Report
```
Sheet: "Monthly Report"
Rows: 50
Columns: 8
Headers: Bold first row
Goal: Clean, readable PDF
```

#### Scenario 2: Wide Table
```
Sheet: "Full Dataset"
Rows: 100
Columns: 25
Headers: Yes
Goal: Fit all columns without cutoff
```

#### Scenario 3: Multiple Sheets
```
Sheets: "Summary", "Details", "Notes"
Varying sizes
Goal: Combined PDF with all sheets
```

## Expected Results

### For Financial Report:
- **Pages:** 3-4 (depending on settings)
- **Orientation:** Portrait recommended
- **Quality:** All text readable, no cutoff

### For Wide Table:
- **Pages:** 2-3 in landscape
- **Orientation:** Landscape required
- **Quality:** May need 70-75% scale

### For Dashboard:
- **Pages:** 1-2 per sheet
- **Orientation:** Auto (mix of portrait/landscape)
- **Quality:** Clean presentation

## Using Example Files

### With VBA:
1. Open the example file in Excel
2. Click "Use Active Workbook"
3. Review analysis
4. Generate PDF

### With Python GUI:
1. Launch application
2. Click "Browse..."
3. Select example file
4. Follow prompts

### With Web App:
1. Open browser to http://localhost:5000
2. Drag and drop example file
3. Review analysis cards
4. Customize and generate

## Creating Sample Data

### Quick Excel Formula Tips:

**Random Numbers:**
```excel
=RANDBETWEEN(1000, 9999)
```

**Random Dates:**
```excel
=TODAY() - RANDBETWEEN(0, 365)
```

**Random Text:**
```excel
=CHOOSE(RANDBETWEEN(1,5), "Alpha", "Beta", "Gamma", "Delta", "Epsilon")
```

**Sequential Data:**
```excel
Row 1: Headers (bold, colored background)
Row 2+: Data formulas
```

## Testing Checklist

When testing with example files:

- [ ] All sheets detected correctly
- [ ] Analysis shows accurate metrics
- [ ] Recommendations make sense
- [ ] Selected sheets process correctly
- [ ] PDF opens without errors
- [ ] Text is selectable in PDF
- [ ] No data is cut off
- [ ] Headers/footers appear if enabled
- [ ] Gridlines show if enabled
- [ ] File size is reasonable
- [ ] PDF renders in all viewers
- [ ] Can copy text from PDF

## Performance Benchmarks

Expected processing times:

| File Size | Sheets | Rows | Time (VBA) | Time (Python) | Time (Web) |
|-----------|--------|------|------------|---------------|------------|
| Small     | 1-2    | <100 | 5-10s      | 3-5s          | 5-8s       |
| Medium    | 3-5    | 100-500 | 15-30s  | 10-15s        | 15-20s     |
| Large     | 5+     | 500-1000 | 30-60s | 20-30s        | 30-45s     |
| Very Large| 10+    | 1000+ | 1-2min    | 45-60s        | 1-2min     |

*Times are approximate and depend on system performance

## Need Help?

- **Analysis not making sense?** Try a simpler file first
- **PDF quality poor?** Check your settings match recommendations
- **Processing slow?** Try fewer sheets or smaller ranges
- **Errors?** Check file isn't corrupted or password-protected

See main documentation for detailed troubleshooting.

---

**Note:** Actual sample files will be added in future updates. For now, create your own using the tips above!
