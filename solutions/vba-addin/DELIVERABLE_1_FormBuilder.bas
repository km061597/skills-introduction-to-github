Attribute VB_Name = "xpdf_FormBuilderModule_v8k2m"
'===============================================================================
' DELIVERABLE 1: UserForm Creation Code
' Purpose: Programmatically creates the complete UserForm with all controls
' Run this ONCE to create the form, then paste Deliverable 2 into the form
'===============================================================================

Option Explicit

Public Sub xpdf_CreateCompleteUserForm_k9m2x()
    On Error GoTo ErrorHandler

    Dim vbProj As Object
    Dim vbComp As Object
    Dim formObj As Object
    Dim ctrl As Object
    Dim formName As String

    formName = "xpdf_MainConverterForm_v7n3k"

    Set vbProj = ThisWorkbook.VBProject

    ' Remove existing form if present
    On Error Resume Next
    Set vbComp = vbProj.VBComponents(formName)
    If Not vbComp Is Nothing Then
        vbProj.VBComponents.Remove vbComp
    End If
    On Error GoTo ErrorHandler

    ' Create new UserForm
    Set vbComp = vbProj.VBComponents.Add(3) ' 3 = vbext_ct_MSForm
    vbComp.Name = formName

    Set formObj = vbComp.Designer

    ' ===== FORM PROPERTIES =====
    With formObj
        .Caption = "Smart Excel to PDF Converter - Enterprise Edition"
        .Width = 780
        .Height = 620
        .BackColor = &HF0F0F0
        .BorderStyle = 0 ' fmBorderStyleNone - we'll add custom
        .Font.Name = "Segoe UI"
        .Font.Size = 9
        .ShowModal = True
        .StartUpPosition = 1 ' CenterOwner
    End With

    ' ===== HEADER PANEL =====
    Set ctrl = formObj.Controls.Add("Forms.Label.1", "xpdf_lblHeaderTitle_m4k8")
    With ctrl
        .Left = 10
        .Top = 10
        .Width = 760
        .Height = 30
        .Caption = "Smart Excel to PDF Converter - Enterprise Edition"
        .Font.Name = "Segoe UI"
        .Font.Size = 14
        .Font.Bold = True
        .ForeColor = &H8B4F1F ' Dark blue
        .BackColor = &HFFFFFF
        .TextAlign = 2 ' fmTextAlignCenter
        .BackStyle = 1 ' fmBackStyleOpaque
    End With

    Set ctrl = formObj.Controls.Add("Forms.Label.1", "xpdf_lblHeaderSubtitle_n7j2")
    With ctrl
        .Left = 10
        .Top = 42
        .Width = 760
        .Height = 18
        .Caption = "Intelligent analysis • Handles dense data & merged cells • Professional output"
        .Font.Name = "Segoe UI"
        .Font.Size = 8
        .ForeColor = &H808080
        .BackColor = &HFFFFFF
        .TextAlign = 2 ' fmTextAlignCenter
        .BackStyle = 1
    End With

    ' ===== FILE SELECTION FRAME =====
    Set ctrl = formObj.Controls.Add("Forms.Frame.1", "xpdf_frameFileSelect_p2m9")
    With ctrl
        .Left = 10
        .Top = 70
        .Width = 760
        .Height = 75
        .Caption = "1. Select Excel File"
        .Font.Name = "Segoe UI"
        .Font.Size = 9
        .Font.Bold = True
        .ForeColor = &H8B4F1F
        .BackColor = &HF0F0F0
    End With

    Set ctrl = formObj.Controls.Add("Forms.TextBox.1", "xpdf_txtFilePath_k3n7", formObj.Controls("xpdf_frameFileSelect_p2m9"))
    With ctrl
        .Left = 10
        .Top = 25
        .Width = 520
        .Height = 24
        .Font.Name = "Segoe UI"
        .Font.Size = 9
        .Locked = True
        .BackColor = &HE0E0E0
        .Text = ""
    End With

    Set ctrl = formObj.Controls.Add("Forms.CommandButton.1", "xpdf_btnBrowseFile_m8k1", formObj.Controls("xpdf_frameFileSelect_p2m9"))
    With ctrl
        .Left = 540
        .Top = 25
        .Width = 100
        .Height = 24
        .Caption = "Browse..."
        .Font.Name = "Segoe UI"
        .Font.Size = 9
        .BackColor = &HE2E2E2
    End With

    Set ctrl = formObj.Controls.Add("Forms.CommandButton.1", "xpdf_btnUseActive_n2j9", formObj.Controls("xpdf_frameFileSelect_p2m9"))
    With ctrl
        .Left = 650
        .Top = 25
        .Width = 100
        .Height = 24
        .Caption = "Use Active"
        .Font.Name = "Segoe UI"
        .Font.Size = 9
        .BackColor = &HE2E2E2
    End With

    ' ===== SHEETS SELECTION FRAME =====
    Set ctrl = formObj.Controls.Add("Forms.Frame.1", "xpdf_frameSheetsSelect_j7n4")
    With ctrl
        .Left = 10
        .Top = 155
        .Width = 370
        .Height = 280
        .Caption = "2. Select Sheets to Convert"
        .Font.Name = "Segoe UI"
        .Font.Size = 9
        .Font.Bold = True
        .ForeColor = &H8B4F1F
        .BackColor = &HF0F0F0
    End With

    Set ctrl = formObj.Controls.Add("Forms.CommandButton.1", "xpdf_btnSelectAllSheets_k8m3", formObj.Controls("xpdf_frameSheetsSelect_j7n4"))
    With ctrl
        .Left = 10
        .Top = 25
        .Width = 85
        .Height = 22
        .Caption = "Select All"
        .Font.Name = "Segoe UI"
        .Font.Size = 8
        .BackColor = &HE2E2E2
    End With

    Set ctrl = formObj.Controls.Add("Forms.CommandButton.1", "xpdf_btnDeselectAllSheets_m3j7", formObj.Controls("xpdf_frameSheetsSelect_j7n4"))
    With ctrl
        .Left = 100
        .Top = 25
        .Width = 85
        .Height = 22
        .Caption = "Clear All"
        .Font.Name = "Segoe UI"
        .Font.Size = 8
        .BackColor = &HE2E2E2
    End With

    Set ctrl = formObj.Controls.Add("Forms.CommandButton.1", "xpdf_btnInvertSelection_n9k2", formObj.Controls("xpdf_frameSheetsSelect_j7n4"))
    With ctrl
        .Left = 190
        .Top = 25
        .Width = 85
        .Height = 22
        .Caption = "Invert"
        .Font.Name = "Segoe UI"
        .Font.Size = 8
        .BackColor = &HE2E2E2
    End With

    Set ctrl = formObj.Controls.Add("Forms.CommandButton.1", "xpdf_btnAnalyzeSheets_p7k4", formObj.Controls("xpdf_frameSheetsSelect_j7n4"))
    With ctrl
        .Left = 280
        .Top = 25
        .Width = 75
        .Height = 22
        .Caption = "Analyze"
        .Font.Name = "Segoe UI"
        .Font.Size = 8
        .Font.Bold = True
        .BackColor = &HC0FFC0
    End With

    Set ctrl = formObj.Controls.Add("Forms.ListBox.1", "xpdf_lstSheets_k2n8", formObj.Controls("xpdf_frameSheetsSelect_j7n4"))
    With ctrl
        .Left = 10
        .Top = 53
        .Width = 345
        .Height = 215
        .Font.Name = "Consolas"
        .Font.Size = 8
        .MultiSelect = 1 ' fmMultiSelectMulti
        .BackColor = &HFFFFFF
    End With

    ' ===== ANALYSIS PANEL =====
    Set ctrl = formObj.Controls.Add("Forms.Frame.1", "xpdf_frameAnalysis_m9j3")
    With ctrl
        .Left = 390
        .Top = 155
        .Width = 380
        .Height = 280
        .Caption = "Sheet Analysis & Recommendations"
        .Font.Name = "Segoe UI"
        .Font.Size = 9
        .Font.Bold = True
        .ForeColor = &H8B4F1F
        .BackColor = &HF0F0F0
    End With

    Set ctrl = formObj.Controls.Add("Forms.TextBox.1", "xpdf_txtAnalysisDisplay_k7m2", formObj.Controls("xpdf_frameAnalysis_m9j3"))
    With ctrl
        .Left = 10
        .Top = 25
        .Width = 360
        .Height = 243
        .Font.Name = "Consolas"
        .Font.Size = 8
        .MultiLine = True
        .ScrollBars = 2 ' fmScrollBarsVertical
        .Locked = True
        .BackColor = &HFFFFF0
        .Text = "Click 'Analyze' to scan selected workbook..." & vbCrLf & vbCrLf & _
                "Features:" & vbCrLf & _
                "• Handles merged cells" & vbCrLf & _
                "• Processes very long text (1000s of chars)" & vbCrLf & _
                "• Smart text wrapping" & vbCrLf & _
                "• Automatic scaling recommendations" & vbCrLf & _
                "• Supports .xlsx, .xlsm, .xlsb formats"
    End With

    ' ===== PDF SETTINGS FRAME =====
    Set ctrl = formObj.Controls.Add("Forms.Frame.1", "xpdf_frameSettings_n4k9")
    With ctrl
        .Left = 10
        .Top = 445
        .Width = 500
        .Height = 130
        .Caption = "3. PDF Settings & Customization"
        .Font.Name = "Segoe UI"
        .Font.Size = 9
        .Font.Bold = True
        .ForeColor = &H8B4F1F
        .BackColor = &HF0F0F0
    End With

    ' Orientation
    Set ctrl = formObj.Controls.Add("Forms.Label.1", "xpdf_lblOrientation_j3m8", formObj.Controls("xpdf_frameSettings_n4k9"))
    With ctrl
        .Left = 10
        .Top = 25
        .Width = 90
        .Height = 18
        .Caption = "Orientation:"
        .Font.Name = "Segoe UI"
        .Font.Size = 9
        .BackStyle = 0
    End With

    Set ctrl = formObj.Controls.Add("Forms.ComboBox.1", "xpdf_cboOrientation_k9n2", formObj.Controls("xpdf_frameSettings_n4k9"))
    With ctrl
        .Left = 105
        .Top = 23
        .Width = 115
        .Height = 20
        .Font.Name = "Segoe UI"
        .Font.Size = 9
        .Style = 2 ' fmStyleDropDownList
        .AddItem "Auto (Smart)"
        .AddItem "Portrait"
        .AddItem "Landscape"
        .ListIndex = 0
    End With

    ' Paper Size
    Set ctrl = formObj.Controls.Add("Forms.Label.1", "xpdf_lblPaperSize_m2k7", formObj.Controls("xpdf_frameSettings_n4k9"))
    With ctrl
        .Left = 230
        .Top = 25
        .Width = 75
        .Height = 18
        .Caption = "Paper Size:"
        .Font.Name = "Segoe UI"
        .Font.Size = 9
        .BackStyle = 0
    End With

    Set ctrl = formObj.Controls.Add("Forms.ComboBox.1", "xpdf_cboPaperSize_n8j3", formObj.Controls("xpdf_frameSettings_n4k9"))
    With ctrl
        .Left = 310
        .Top = 23
        .Width = 95
        .Height = 20
        .Font.Name = "Segoe UI"
        .Font.Size = 9
        .Style = 2
        .AddItem "Letter"
        .AddItem "Legal"
        .AddItem "A4"
        .AddItem "A3"
        .AddItem "Tabloid"
        .ListIndex = 0
    End With

    ' Scaling Mode
    Set ctrl = formObj.Controls.Add("Forms.CheckBox.1", "xpdf_chkFitToWidth_k3m9", formObj.Controls("xpdf_frameSettings_n4k9"))
    With ctrl
        .Left = 10
        .Top = 53
        .Width = 210
        .Height = 18
        .Caption = "Fit to Page Width (Recommended)"
        .Font.Name = "Segoe UI"
        .Font.Size = 9
        .Value = True
        .BackStyle = 0
    End With

    Set ctrl = formObj.Controls.Add("Forms.Label.1", "xpdf_lblScale_m7n2", formObj.Controls("xpdf_frameSettings_n4k9"))
    With ctrl
        .Left = 230
        .Top = 53
        .Width = 75
        .Height = 18
        .Caption = "Scale %:"
        .Font.Name = "Segoe UI"
        .Font.Size = 9
        .BackStyle = 0
    End With

    Set ctrl = formObj.Controls.Add("Forms.SpinButton.1", "xpdf_spinScale_k8j4", formObj.Controls("xpdf_frameSettings_n4k9"))
    With ctrl
        .Left = 385
        .Top = 51
        .Width = 15
        .Height = 20
        .Min = 10
        .Max = 200
        .Value = 100
        .SmallChange = 5
    End With

    Set ctrl = formObj.Controls.Add("Forms.TextBox.1", "xpdf_txtScale_n3k7", formObj.Controls("xpdf_frameSettings_n4k9"))
    With ctrl
        .Left = 310
        .Top = 51
        .Width = 70
        .Height = 20
        .Font.Name = "Segoe UI"
        .Font.Size = 9
        .Text = "100"
        .TextAlign = 3 ' fmTextAlignRight
    End With

    ' Margins Section
    Set ctrl = formObj.Controls.Add("Forms.Label.1", "xpdf_lblMarginsHeader_j9m3", formObj.Controls("xpdf_frameSettings_n4k9"))
    With ctrl
        .Left = 10
        .Top = 80
        .Width = 100
        .Height = 18
        .Caption = "Margins (inches):"
        .Font.Name = "Segoe UI"
        .Font.Size = 9
        .Font.Bold = True
        .BackStyle = 0
    End With

    ' Left Margin
    Set ctrl = formObj.Controls.Add("Forms.Label.1", "xpdf_lblMarginLeft_k2n9", formObj.Controls("xpdf_frameSettings_n4k9"))
    With ctrl
        .Left = 10
        .Top = 102
        .Width = 35
        .Height = 18
        .Caption = "Left:"
        .Font.Name = "Segoe UI"
        .Font.Size = 8
        .BackStyle = 0
    End With

    Set ctrl = formObj.Controls.Add("Forms.TextBox.1", "xpdf_txtMarginLeft_m9k3", formObj.Controls("xpdf_frameSettings_n4k9"))
    With ctrl
        .Left = 45
        .Top = 100
        .Width = 50
        .Height = 20
        .Font.Name = "Segoe UI"
        .Font.Size = 9
        .Text = "0.25"
        .TextAlign = 3
    End With

    ' Right Margin
    Set ctrl = formObj.Controls.Add("Forms.Label.1", "xpdf_lblMarginRight_n7j2", formObj.Controls("xpdf_frameSettings_n4k9"))
    With ctrl
        .Left = 105
        .Top = 102
        .Width = 40
        .Height = 18
        .Caption = "Right:"
        .Font.Name = "Segoe UI"
        .Font.Size = 8
        .BackStyle = 0
    End With

    Set ctrl = formObj.Controls.Add("Forms.TextBox.1", "xpdf_txtMarginRight_k8m2", formObj.Controls("xpdf_frameSettings_n4k9"))
    With ctrl
        .Left = 145
        .Top = 100
        .Width = 50
        .Height = 20
        .Font.Name = "Segoe UI"
        .Font.Size = 9
        .Text = "0.25"
        .TextAlign = 3
    End With

    ' Top Margin
    Set ctrl = formObj.Controls.Add("Forms.Label.1", "xpdf_lblMarginTop_j4k8", formObj.Controls("xpdf_frameSettings_n4k9"))
    With ctrl
        .Left = 205
        .Top = 102
        .Width = 35
        .Height = 18
        .Caption = "Top:"
        .Font.Name = "Segoe UI"
        .Font.Size = 8
        .BackStyle = 0
    End With

    Set ctrl = formObj.Controls.Add("Forms.TextBox.1", "xpdf_txtMarginTop_m3n7", formObj.Controls("xpdf_frameSettings_n4k9"))
    With ctrl
        .Left = 240
        .Top = 100
        .Width = 50
        .Height = 20
        .Font.Name = "Segoe UI"
        .Font.Size = 9
        .Text = "0.75"
        .TextAlign = 3
    End With

    ' Bottom Margin
    Set ctrl = formObj.Controls.Add("Forms.Label.1", "xpdf_lblMarginBottom_k9j3", formObj.Controls("xpdf_frameSettings_n4k9"))
    With ctrl
        .Left = 300
        .Top = 102
        .Width = 50
        .Height = 18
        .Caption = "Bottom:"
        .Font.Name = "Segoe UI"
        .Font.Size = 8
        .BackStyle = 0
    End With

    Set ctrl = formObj.Controls.Add("Forms.TextBox.1", "xpdf_txtMarginBottom_n2k8", formObj.Controls("xpdf_frameSettings_n4k9"))
    With ctrl
        .Left = 355
        .Top = 100
        .Width = 50
        .Height = 20
        .Font.Name = "Segoe UI"
        .Font.Size = 9
        .Text = "0.75"
        .TextAlign = 3
    End With

    ' ===== OPTIONS FRAME =====
    Set ctrl = formObj.Controls.Add("Forms.Frame.1", "xpdf_frameOptions_j8n4")
    With ctrl
        .Left = 520
        .Top = 445
        .Width = 250
        .Height = 130
        .Caption = "Advanced Options"
        .Font.Name = "Segoe UI"
        .Font.Size = 9
        .Font.Bold = True
        .ForeColor = &H8B4F1F
        .BackColor = &HF0F0F0
    End With

    Set ctrl = formObj.Controls.Add("Forms.CheckBox.1", "xpdf_chkIncludeHeaders_m4k9", formObj.Controls("xpdf_frameOptions_j8n4"))
    With ctrl
        .Left = 10
        .Top = 25
        .Width = 230
        .Height = 16
        .Caption = "Include Headers/Footers"
        .Font.Name = "Segoe UI"
        .Font.Size = 8
        .Value = True
        .BackStyle = 0
    End With

    Set ctrl = formObj.Controls.Add("Forms.CheckBox.1", "xpdf_chkPrintGridlines_n7k3", formObj.Controls("xpdf_frameOptions_j8n4"))
    With ctrl
        .Left = 10
        .Top = 45
        .Width = 230
        .Height = 16
        .Caption = "Print Gridlines"
        .Font.Name = "Segoe UI"
        .Font.Size = 8
        .Value = False
        .BackStyle = 0
    End With

    Set ctrl = formObj.Controls.Add("Forms.CheckBox.1", "xpdf_chkWrapLongText_k8m4", formObj.Controls("xpdf_frameOptions_j8n4"))
    With ctrl
        .Left = 10
        .Top = 65
        .Width = 230
        .Height = 16
        .Caption = "Wrap Long Text (Dense Data)"
        .Font.Name = "Segoe UI"
        .Font.Size = 8
        .Value = True
        .BackStyle = 0
    End With

    Set ctrl = formObj.Controls.Add("Forms.CheckBox.1", "xpdf_chkHandleMerged_m9j2", formObj.Controls("xpdf_frameOptions_j8n4"))
    With ctrl
        .Left = 10
        .Top = 85
        .Width = 230
        .Height = 16
        .Caption = "Optimize Merged Cells"
        .Font.Name = "Segoe UI"
        .Font.Size = 8
        .Value = True
        .BackStyle = 0
    End With

    Set ctrl = formObj.Controls.Add("Forms.CheckBox.1", "xpdf_chkHighQuality_k3n8", formObj.Controls("xpdf_frameOptions_j8n4"))
    With ctrl
        .Left = 10
        .Top = 105
        .Width = 230
        .Height = 16
        .Caption = "High Quality (600 DPI)"
        .Font.Name = "Segoe UI"
        .Font.Size = 8
        .Value = True
        .BackStyle = 0
    End With

    ' ===== PROGRESS BAR =====
    Set ctrl = formObj.Controls.Add("Forms.Label.1", "xpdf_lblProgressBar_n9k7")
    With ctrl
        .Left = 10
        .Top = 583
        .Width = 760
        .Height = 6
        .BackColor = &H8B4F1F
        .Caption = ""
        .SpecialEffect = 0
        .Visible = False
    End With

    ' ===== STATUS LABEL =====
    Set ctrl = formObj.Controls.Add("Forms.Label.1", "xpdf_lblStatus_k7m9")
    With ctrl
        .Left = 10
        .Top = 595
        .Width = 550
        .Height = 18
        .Caption = "Ready"
        .Font.Name = "Segoe UI"
        .Font.Size = 8
        .ForeColor = &H808080
        .BackStyle = 0
    End With

    ' ===== ACTION BUTTONS =====
    Set ctrl = formObj.Controls.Add("Forms.CommandButton.1", "xpdf_btnGeneratePDF_m8k3")
    With ctrl
        .Left = 570
        .Top = 590
        .Width = 100
        .Height = 28
        .Caption = "Generate PDF"
        .Font.Name = "Segoe UI"
        .Font.Size = 9
        .Font.Bold = True
        .BackColor = &HC0FFC0
    End With

    Set ctrl = formObj.Controls.Add("Forms.CommandButton.1", "xpdf_btnCancel_n4j9")
    With ctrl
        .Left = 675
        .Top = 590
        .Width = 95
        .Height = 28
        .Caption = "Close"
        .Font.Name = "Segoe UI"
        .Font.Size = 9
        .BackColor = &HE0E0E0
    End With

    MsgBox "UserForm '" & formName & "' created successfully!" & vbCrLf & vbCrLf & _
           "Next steps:" & vbCrLf & _
           "1. Open the VBA Editor (Alt+F11)" & vbCrLf & _
           "2. Find the form: " & formName & vbCrLf & _
           "3. Double-click to open it" & vbCrLf & _
           "4. Right-click > View Code" & vbCrLf & _
           "5. Paste DELIVERABLE 2 code into the code window" & vbCrLf & _
           "6. Then add DELIVERABLE 3 as a new standard module" & vbCrLf & _
           "7. Then add DELIVERABLE 4 as a new class module", vbInformation, "Form Created"

    Exit Sub

ErrorHandler:
    MsgBox "Error creating UserForm: " & Err.Description & vbCrLf & _
           "Error Number: " & Err.Number & vbCrLf & vbCrLf & _
           "Make sure 'Trust access to the VBA project object model' is enabled in:" & vbCrLf & _
           "File > Options > Trust Center > Trust Center Settings > Macro Settings", _
           vbCritical, "Error"
End Sub
