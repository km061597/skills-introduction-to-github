Attribute VB_Name = "xpdf_FormBuilderModule_v8k2m"
'===============================================================================
' DELIVERABLE 1: UserForm Creation Code - MINIMAL SAFE VERSION
' Purpose: Creates UserForm with only safe properties
' All styling/formatting happens in DELIVERABLE 2's Initialize event
'===============================================================================

Option Explicit

Public Sub xpdf_CreateCompleteUserForm_k9m2x()
    On Error GoTo ErrorHandler

    Dim vbProj As Object
    Dim vbComp As Object
    Dim formObj As Object
    Dim ctrl As Object
    Dim formName As String

    ' Frame references
    Dim frameFileSelect As Object
    Dim frameSheetsSelect As Object
    Dim frameAnalysis As Object
    Dim frameSettings As Object
    Dim frameOptions As Object

    formName = "xpdf_MainConverterForm_v7n3k"
    Set vbProj = ThisWorkbook.VBProject

    ' Remove existing form
    On Error Resume Next
    Set vbComp = vbProj.VBComponents(formName)
    If Not vbComp Is Nothing Then vbProj.VBComponents.Remove vbComp
    On Error GoTo ErrorHandler

    ' Create form
    Set vbComp = vbProj.VBComponents.Add(3)
    vbComp.Name = formName
    Set formObj = vbComp.Designer

    ' FORM - only size and caption
    formObj.Caption = "Smart Excel to PDF Converter"
    formObj.Width = 780
    formObj.Height = 620

    ' HEADER TITLE
    Set ctrl = formObj.Controls.Add("Forms.Label.1", "xpdf_lblHeaderTitle_m4k8")
    ctrl.Left = 10: ctrl.Top = 10: ctrl.Width = 760: ctrl.Height = 30
    ctrl.Caption = "Smart Excel to PDF Converter - Enterprise Edition"

    ' HEADER SUBTITLE
    Set ctrl = formObj.Controls.Add("Forms.Label.1", "xpdf_lblHeaderSubtitle_n7j2")
    ctrl.Left = 10: ctrl.Top = 42: ctrl.Width = 760: ctrl.Height = 18
    ctrl.Caption = "Intelligent analysis - Handles dense data & merged cells"

    ' ===== FILE SELECTION FRAME =====
    Set frameFileSelect = formObj.Controls.Add("Forms.Frame.1", "xpdf_frameFileSelect_p2m9")
    frameFileSelect.Left = 10: frameFileSelect.Top = 70
    frameFileSelect.Width = 760: frameFileSelect.Height = 75
    frameFileSelect.Caption = "1. Select Excel File"

    Set ctrl = frameFileSelect.Controls.Add("Forms.TextBox.1", "xpdf_txtFilePath_k3n7")
    ctrl.Left = 10: ctrl.Top = 25: ctrl.Width = 520: ctrl.Height = 24

    Set ctrl = frameFileSelect.Controls.Add("Forms.CommandButton.1", "xpdf_btnBrowseFile_m8k1")
    ctrl.Left = 540: ctrl.Top = 25: ctrl.Width = 100: ctrl.Height = 24
    ctrl.Caption = "Browse..."

    Set ctrl = frameFileSelect.Controls.Add("Forms.CommandButton.1", "xpdf_btnUseActive_n2j9")
    ctrl.Left = 650: ctrl.Top = 25: ctrl.Width = 100: ctrl.Height = 24
    ctrl.Caption = "Use Active"

    ' ===== SHEETS SELECTION FRAME =====
    Set frameSheetsSelect = formObj.Controls.Add("Forms.Frame.1", "xpdf_frameSheetsSelect_j7n4")
    frameSheetsSelect.Left = 10: frameSheetsSelect.Top = 155
    frameSheetsSelect.Width = 370: frameSheetsSelect.Height = 280
    frameSheetsSelect.Caption = "2. Select Sheets"

    Set ctrl = frameSheetsSelect.Controls.Add("Forms.CommandButton.1", "xpdf_btnSelectAllSheets_k8m3")
    ctrl.Left = 10: ctrl.Top = 25: ctrl.Width = 85: ctrl.Height = 22
    ctrl.Caption = "Select All"

    Set ctrl = frameSheetsSelect.Controls.Add("Forms.CommandButton.1", "xpdf_btnDeselectAllSheets_m3j7")
    ctrl.Left = 100: ctrl.Top = 25: ctrl.Width = 85: ctrl.Height = 22
    ctrl.Caption = "Clear All"

    Set ctrl = frameSheetsSelect.Controls.Add("Forms.CommandButton.1", "xpdf_btnInvertSelection_n9k2")
    ctrl.Left = 190: ctrl.Top = 25: ctrl.Width = 85: ctrl.Height = 22
    ctrl.Caption = "Invert"

    Set ctrl = frameSheetsSelect.Controls.Add("Forms.CommandButton.1", "xpdf_btnAnalyzeSheets_p7k4")
    ctrl.Left = 280: ctrl.Top = 25: ctrl.Width = 75: ctrl.Height = 22
    ctrl.Caption = "Analyze"

    Set ctrl = frameSheetsSelect.Controls.Add("Forms.ListBox.1", "xpdf_lstSheets_k2n8")
    ctrl.Left = 10: ctrl.Top = 53: ctrl.Width = 345: ctrl.Height = 215

    ' ===== ANALYSIS FRAME =====
    Set frameAnalysis = formObj.Controls.Add("Forms.Frame.1", "xpdf_frameAnalysis_m9j3")
    frameAnalysis.Left = 390: frameAnalysis.Top = 155
    frameAnalysis.Width = 380: frameAnalysis.Height = 280
    frameAnalysis.Caption = "Analysis & Recommendations"

    Set ctrl = frameAnalysis.Controls.Add("Forms.TextBox.1", "xpdf_txtAnalysisDisplay_k7m2")
    ctrl.Left = 10: ctrl.Top = 25: ctrl.Width = 360: ctrl.Height = 243

    ' ===== SETTINGS FRAME =====
    Set frameSettings = formObj.Controls.Add("Forms.Frame.1", "xpdf_frameSettings_n4k9")
    frameSettings.Left = 10: frameSettings.Top = 445
    frameSettings.Width = 500: frameSettings.Height = 130
    frameSettings.Caption = "3. PDF Settings"

    Set ctrl = frameSettings.Controls.Add("Forms.Label.1", "xpdf_lblOrientation_j3m8")
    ctrl.Left = 10: ctrl.Top = 25: ctrl.Width = 90: ctrl.Height = 18
    ctrl.Caption = "Orientation:"

    Set ctrl = frameSettings.Controls.Add("Forms.ComboBox.1", "xpdf_cboOrientation_k9n2")
    ctrl.Left = 105: ctrl.Top = 23: ctrl.Width = 115: ctrl.Height = 20

    Set ctrl = frameSettings.Controls.Add("Forms.Label.1", "xpdf_lblPaperSize_m2k7")
    ctrl.Left = 230: ctrl.Top = 25: ctrl.Width = 75: ctrl.Height = 18
    ctrl.Caption = "Paper Size:"

    Set ctrl = frameSettings.Controls.Add("Forms.ComboBox.1", "xpdf_cboPaperSize_n8j3")
    ctrl.Left = 310: ctrl.Top = 23: ctrl.Width = 95: ctrl.Height = 20

    Set ctrl = frameSettings.Controls.Add("Forms.CheckBox.1", "xpdf_chkFitToWidth_k3m9")
    ctrl.Left = 10: ctrl.Top = 53: ctrl.Width = 210: ctrl.Height = 18
    ctrl.Caption = "Fit to Page Width"

    Set ctrl = frameSettings.Controls.Add("Forms.Label.1", "xpdf_lblScale_m7n2")
    ctrl.Left = 230: ctrl.Top = 53: ctrl.Width = 75: ctrl.Height = 18
    ctrl.Caption = "Scale %:"

    Set ctrl = frameSettings.Controls.Add("Forms.TextBox.1", "xpdf_txtScale_n3k7")
    ctrl.Left = 310: ctrl.Top = 51: ctrl.Width = 70: ctrl.Height = 20

    Set ctrl = frameSettings.Controls.Add("Forms.SpinButton.1", "xpdf_spinScale_k8j4")
    ctrl.Left = 385: ctrl.Top = 51: ctrl.Width = 15: ctrl.Height = 20

    Set ctrl = frameSettings.Controls.Add("Forms.Label.1", "xpdf_lblMarginsHeader_j9m3")
    ctrl.Left = 10: ctrl.Top = 80: ctrl.Width = 100: ctrl.Height = 18
    ctrl.Caption = "Margins (inches):"

    Set ctrl = frameSettings.Controls.Add("Forms.Label.1", "xpdf_lblMarginLeft_k2n9")
    ctrl.Left = 10: ctrl.Top = 102: ctrl.Width = 35: ctrl.Height = 18
    ctrl.Caption = "Left:"

    Set ctrl = frameSettings.Controls.Add("Forms.TextBox.1", "xpdf_txtMarginLeft_m9k3")
    ctrl.Left = 45: ctrl.Top = 100: ctrl.Width = 50: ctrl.Height = 20

    Set ctrl = frameSettings.Controls.Add("Forms.Label.1", "xpdf_lblMarginRight_n7j2")
    ctrl.Left = 105: ctrl.Top = 102: ctrl.Width = 40: ctrl.Height = 18
    ctrl.Caption = "Right:"

    Set ctrl = frameSettings.Controls.Add("Forms.TextBox.1", "xpdf_txtMarginRight_k8m2")
    ctrl.Left = 145: ctrl.Top = 100: ctrl.Width = 50: ctrl.Height = 20

    Set ctrl = frameSettings.Controls.Add("Forms.Label.1", "xpdf_lblMarginTop_j4k8")
    ctrl.Left = 205: ctrl.Top = 102: ctrl.Width = 35: ctrl.Height = 18
    ctrl.Caption = "Top:"

    Set ctrl = frameSettings.Controls.Add("Forms.TextBox.1", "xpdf_txtMarginTop_m3n7")
    ctrl.Left = 240: ctrl.Top = 100: ctrl.Width = 50: ctrl.Height = 20

    Set ctrl = frameSettings.Controls.Add("Forms.Label.1", "xpdf_lblMarginBottom_k9j3")
    ctrl.Left = 300: ctrl.Top = 102: ctrl.Width = 50: ctrl.Height = 18
    ctrl.Caption = "Bottom:"

    Set ctrl = frameSettings.Controls.Add("Forms.TextBox.1", "xpdf_txtMarginBottom_n2k8")
    ctrl.Left = 355: ctrl.Top = 100: ctrl.Width = 50: ctrl.Height = 20

    ' ===== OPTIONS FRAME =====
    Set frameOptions = formObj.Controls.Add("Forms.Frame.1", "xpdf_frameOptions_j8n4")
    frameOptions.Left = 520: frameOptions.Top = 445
    frameOptions.Width = 250: frameOptions.Height = 130
    frameOptions.Caption = "Advanced Options"

    Set ctrl = frameOptions.Controls.Add("Forms.CheckBox.1", "xpdf_chkIncludeHeaders_m4k9")
    ctrl.Left = 10: ctrl.Top = 25: ctrl.Width = 230: ctrl.Height = 16
    ctrl.Caption = "Include Headers/Footers"

    Set ctrl = frameOptions.Controls.Add("Forms.CheckBox.1", "xpdf_chkPrintGridlines_n7k3")
    ctrl.Left = 10: ctrl.Top = 45: ctrl.Width = 230: ctrl.Height = 16
    ctrl.Caption = "Print Gridlines"

    Set ctrl = frameOptions.Controls.Add("Forms.CheckBox.1", "xpdf_chkWrapLongText_k8m4")
    ctrl.Left = 10: ctrl.Top = 65: ctrl.Width = 230: ctrl.Height = 16
    ctrl.Caption = "Wrap Long Text"

    Set ctrl = frameOptions.Controls.Add("Forms.CheckBox.1", "xpdf_chkHandleMerged_m9j2")
    ctrl.Left = 10: ctrl.Top = 85: ctrl.Width = 230: ctrl.Height = 16
    ctrl.Caption = "Optimize Merged Cells"

    Set ctrl = frameOptions.Controls.Add("Forms.CheckBox.1", "xpdf_chkHighQuality_k3n8")
    ctrl.Left = 10: ctrl.Top = 105: ctrl.Width = 230: ctrl.Height = 16
    ctrl.Caption = "High Quality (600 DPI)"

    ' ===== PROGRESS BAR =====
    Set ctrl = formObj.Controls.Add("Forms.Label.1", "xpdf_lblProgressBar_n9k7")
    ctrl.Left = 10: ctrl.Top = 583: ctrl.Width = 760: ctrl.Height = 6

    ' ===== STATUS LABEL =====
    Set ctrl = formObj.Controls.Add("Forms.Label.1", "xpdf_lblStatus_k7m9")
    ctrl.Left = 10: ctrl.Top = 595: ctrl.Width = 550: ctrl.Height = 18
    ctrl.Caption = "Ready"

    ' ===== ACTION BUTTONS =====
    Set ctrl = formObj.Controls.Add("Forms.CommandButton.1", "xpdf_btnGeneratePDF_m8k3")
    ctrl.Left = 570: ctrl.Top = 590: ctrl.Width = 100: ctrl.Height = 28
    ctrl.Caption = "Generate PDF"

    Set ctrl = formObj.Controls.Add("Forms.CommandButton.1", "xpdf_btnCancel_n4j9")
    ctrl.Left = 675: ctrl.Top = 590: ctrl.Width = 95: ctrl.Height = 28
    ctrl.Caption = "Close"

    MsgBox "UserForm created successfully!" & vbCrLf & vbCrLf & _
           "Next: Paste DELIVERABLE 2 into the form's code window", vbInformation

    Exit Sub

ErrorHandler:
    MsgBox "Error: " & Err.Description & " (Number: " & Err.Number & ")" & vbCrLf & vbCrLf & _
           "Ensure 'Trust access to VBA project object model' is enabled", vbCritical
End Sub
