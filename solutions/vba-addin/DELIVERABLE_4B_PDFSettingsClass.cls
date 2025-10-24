VERSION 1.0 CLASS
BEGIN
  MultiUse = -1  'True
END
Attribute VB_Name = "xpdf_PDFSettingsClass_k8n4"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = False
Attribute VB_Exposed = False
'===============================================================================
' DELIVERABLE 4B: PDF Settings Class Module
' Purpose: Stores all PDF generation settings and preferences
' Instructions: Insert > Class Module, name it exactly as shown above, paste code
'===============================================================================

Option Explicit

' Private member variables
Private pvarOutputPath_k9m2x As String
Private pvarOrientation_n7j3x As String
Private pvarPaperSize_m8k4x As XlPaperSize
Private pvarFitToWidth_k3n9x As Boolean
Private pvarScalePercent_m7n2x As Long
Private pvarMarginLeft_k2n8x As Double
Private pvarMarginRight_n9k3x As Double
Private pvarMarginTop_k8m9x As Double
Private pvarMarginBottom_m3k7x As Double
Private pvarIncludeHeaders_n7k2x As Boolean
Private pvarPrintGridlines_k9m8x As Boolean
Private pvarWrapLongText_m2n7x As Boolean
Private pvarHandleMergedCells_k8n3x As Boolean
Private pvarHighQuality_n4k9x As Boolean

'===============================================================================
' PROPERTY: OutputPath_k9m2
'===============================================================================

Public Property Get OutputPath_k9m2() As String
    OutputPath_k9m2 = pvarOutputPath_k9m2x
End Property

Public Property Let OutputPath_k9m2(ByVal vData As String)
    pvarOutputPath_k9m2x = vData
End Property

'===============================================================================
' PROPERTY: Orientation_n7j3
'===============================================================================

Public Property Get Orientation_n7j3() As String
    Orientation_n7j3 = pvarOrientation_n7j3x
End Property

Public Property Let Orientation_n7j3(ByVal vData As String)
    pvarOrientation_n7j3x = vData
End Property

'===============================================================================
' PROPERTY: PaperSize_m8k4
'===============================================================================

Public Property Get PaperSize_m8k4() As XlPaperSize
    PaperSize_m8k4 = pvarPaperSize_m8k4x
End Property

Public Property Let PaperSize_m8k4(ByVal vData As XlPaperSize)
    pvarPaperSize_m8k4x = vData
End Property

'===============================================================================
' PROPERTY: FitToWidth_k3n9
'===============================================================================

Public Property Get FitToWidth_k3n9() As Boolean
    FitToWidth_k3n9 = pvarFitToWidth_k3n9x
End Property

Public Property Let FitToWidth_k3n9(ByVal vData As Boolean)
    pvarFitToWidth_k3n9x = vData
End Property

'===============================================================================
' PROPERTY: ScalePercent_m7n2
'===============================================================================

Public Property Get ScalePercent_m7n2() As Long
    ScalePercent_m7n2 = pvarScalePercent_m7n2x
End Property

Public Property Let ScalePercent_m7n2(ByVal vData As Long)
    If vData < 10 Then vData = 10
    If vData > 200 Then vData = 200
    pvarScalePercent_m7n2x = vData
End Property

'===============================================================================
' PROPERTY: MarginLeft_k2n8
'===============================================================================

Public Property Get MarginLeft_k2n8() As Double
    MarginLeft_k2n8 = pvarMarginLeft_k2n8x
End Property

Public Property Let MarginLeft_k2n8(ByVal vData As Double)
    If vData < 0 Then vData = 0
    If vData > 3 Then vData = 3
    pvarMarginLeft_k2n8x = vData
End Property

'===============================================================================
' PROPERTY: MarginRight_n9k3
'===============================================================================

Public Property Get MarginRight_n9k3() As Double
    MarginRight_n9k3 = pvarMarginRight_n9k3x
End Property

Public Property Let MarginRight_n9k3(ByVal vData As Double)
    If vData < 0 Then vData = 0
    If vData > 3 Then vData = 3
    pvarMarginRight_n9k3x = vData
End Property

'===============================================================================
' PROPERTY: MarginTop_k8m9
'===============================================================================

Public Property Get MarginTop_k8m9() As Double
    MarginTop_k8m9 = pvarMarginTop_k8m9x
End Property

Public Property Let MarginTop_k8m9(ByVal vData As Double)
    If vData < 0 Then vData = 0
    If vData > 3 Then vData = 3
    pvarMarginTop_k8m9x = vData
End Property

'===============================================================================
' PROPERTY: MarginBottom_m3k7
'===============================================================================

Public Property Get MarginBottom_m3k7() As Double
    MarginBottom_m3k7 = pvarMarginBottom_m3k7x
End Property

Public Property Let MarginBottom_m3k7(ByVal vData As Double)
    If vData < 0 Then vData = 0
    If vData > 3 Then vData = 3
    pvarMarginBottom_m3k7x = vData
End Property

'===============================================================================
' PROPERTY: IncludeHeaders_n7k2
'===============================================================================

Public Property Get IncludeHeaders_n7k2() As Boolean
    IncludeHeaders_n7k2 = pvarIncludeHeaders_n7k2x
End Property

Public Property Let IncludeHeaders_n7k2(ByVal vData As Boolean)
    pvarIncludeHeaders_n7k2x = vData
End Property

'===============================================================================
' PROPERTY: PrintGridlines_k9m8
'===============================================================================

Public Property Get PrintGridlines_k9m8() As Boolean
    PrintGridlines_k9m8 = pvarPrintGridlines_k9m8x
End Property

Public Property Let PrintGridlines_k9m8(ByVal vData As Boolean)
    pvarPrintGridlines_k9m8x = vData
End Property

'===============================================================================
' PROPERTY: WrapLongText_m2n7
'===============================================================================

Public Property Get WrapLongText_m2n7() As Boolean
    WrapLongText_m2n7 = pvarWrapLongText_m2n7x
End Property

Public Property Let WrapLongText_m2n7(ByVal vData As Boolean)
    pvarWrapLongText_m2n7x = vData
End Property

'===============================================================================
' PROPERTY: HandleMergedCells_k8n3
'===============================================================================

Public Property Get HandleMergedCells_k8n3() As Boolean
    HandleMergedCells_k8n3 = pvarHandleMergedCells_k8n3x
End Property

Public Property Let HandleMergedCells_k8n3(ByVal vData As Boolean)
    pvarHandleMergedCells_k8n3x = vData
End Property

'===============================================================================
' PROPERTY: HighQuality_n4k9
'===============================================================================

Public Property Get HighQuality_n4k9() As Boolean
    HighQuality_n4k9 = pvarHighQuality_n4k9x
End Property

Public Property Let HighQuality_n4k9(ByVal vData As Boolean)
    pvarHighQuality_n4k9x = vData
End Property

'===============================================================================
' CLASS INITIALIZATION
'===============================================================================

Private Sub Class_Initialize()
    pvarOutputPath_k9m2x = ""
    pvarOrientation_n7j3x = "Auto"
    pvarPaperSize_m8k4x = xlPaperLetter
    pvarFitToWidth_k3n9x = True
    pvarScalePercent_m7n2x = 100
    pvarMarginLeft_k2n8x = 0.25
    pvarMarginRight_n9k3x = 0.25
    pvarMarginTop_k8m9x = 0.75
    pvarMarginBottom_m3k7x = 0.75
    pvarIncludeHeaders_n7k2x = True
    pvarPrintGridlines_k9m8x = False
    pvarWrapLongText_m2n7x = True
    pvarHandleMergedCells_k8n3x = True
    pvarHighQuality_n4k9x = True
End Sub

'===============================================================================
' CLASS TERMINATION
'===============================================================================

Private Sub Class_Terminate()
    ' Cleanup if needed
End Sub

'===============================================================================
' PUBLIC METHODS
'===============================================================================

Public Function xpdf_ValidateSettings_k9m7() As Boolean
    xpdf_ValidateSettings_k9m7 = False

    ' Validate output path
    If Len(pvarOutputPath_k9m2x) = 0 Then Exit Function

    ' Validate orientation
    Dim orientUpper_k8m3 As String
    orientUpper_k8m3 = UCase(pvarOrientation_n7j3x)

    If orientUpper_k8m3 <> "AUTO" And orientUpper_k8m3 <> "PORTRAIT" And orientUpper_k8m3 <> "LANDSCAPE" Then
        Exit Function
    End If

    ' Validate scale
    If pvarScalePercent_m7n2x < 10 Or pvarScalePercent_m7n2x > 200 Then Exit Function

    ' Validate margins
    If pvarMarginLeft_k2n8x < 0 Or pvarMarginLeft_k2n8x > 3 Then Exit Function
    If pvarMarginRight_n9k3x < 0 Or pvarMarginRight_n9k3x > 3 Then Exit Function
    If pvarMarginTop_k8m9x < 0 Or pvarMarginTop_k8m9x > 3 Then Exit Function
    If pvarMarginBottom_m3k7x < 0 Or pvarMarginBottom_m3k7x > 3 Then Exit Function

    xpdf_ValidateSettings_k9m7 = True
End Function

Public Sub xpdf_ResetToDefaults_m8k4()
    pvarOutputPath_k9m2x = ""
    pvarOrientation_n7j3x = "Auto"
    pvarPaperSize_m8k4x = xlPaperLetter
    pvarFitToWidth_k3n9x = True
    pvarScalePercent_m7n2x = 100
    pvarMarginLeft_k2n8x = 0.25
    pvarMarginRight_n9k3x = 0.25
    pvarMarginTop_k8m9x = 0.75
    pvarMarginBottom_m3k7x = 0.75
    pvarIncludeHeaders_n7k2x = True
    pvarPrintGridlines_k9m8x = False
    pvarWrapLongText_m2n7x = True
    pvarHandleMergedCells_k8n3x = True
    pvarHighQuality_n4k9x = True
End Sub

Public Function xpdf_GetPaperSizeName_k9n3() As String
    Select Case pvarPaperSize_m8k4x
        Case xlPaperLetter
            xpdf_GetPaperSizeName_k9n3 = "Letter"
        Case xlPaperLegal
            xpdf_GetPaperSizeName_k9n3 = "Legal"
        Case xlPaperA4
            xpdf_GetPaperSizeName_k9n3 = "A4"
        Case xlPaperA3
            xpdf_GetPaperSizeName_k9n3 = "A3"
        Case xlPaperTabloid
            xpdf_GetPaperSizeName_k9n3 = "Tabloid"
        Case Else
            xpdf_GetPaperSizeName_k9n3 = "Unknown"
    End Select
End Function

Public Function xpdf_GetSettingsSummary_n7k8() As String
    Dim summary_k9m2 As String

    summary_k9m2 = "PDF Settings Summary:" & vbCrLf
    summary_k9m2 = summary_k9m2 & "  Orientation: " & pvarOrientation_n7j3x & vbCrLf
    summary_k9m2 = summary_k9m2 & "  Paper: " & xpdf_GetPaperSizeName_k9n3 & vbCrLf

    If pvarFitToWidth_k3n9x Then
        summary_k9m2 = summary_k9m2 & "  Scaling: Fit to Width" & vbCrLf
    Else
        summary_k9m2 = summary_k9m2 & "  Scaling: " & pvarScalePercent_m7n2x & "%" & vbCrLf
    End If

    summary_k9m2 = summary_k9m2 & "  Margins: L=" & pvarMarginLeft_k2n8x & _
                                  ", R=" & pvarMarginRight_n9k3x & _
                                  ", T=" & pvarMarginTop_k8m9x & _
                                  ", B=" & pvarMarginBottom_m3k7x & vbCrLf
    summary_k9m2 = summary_k9m2 & "  Headers: " & IIf(pvarIncludeHeaders_n7k2x, "Yes", "No") & vbCrLf
    summary_k9m2 = summary_k9m2 & "  Gridlines: " & IIf(pvarPrintGridlines_k9m8x, "Yes", "No") & vbCrLf
    summary_k9m2 = summary_k9m2 & "  Quality: " & IIf(pvarHighQuality_n4k9x, "High (600 DPI)", "Standard (300 DPI)")

    xpdf_GetSettingsSummary_n7k8 = summary_k9m2
End Function

Public Function xpdf_Clone_m8k4() As xpdf_PDFSettingsClass_k8n4
    Dim newObj_k9m2 As xpdf_PDFSettingsClass_k8n4
    Set newObj_k9m2 = New xpdf_PDFSettingsClass_k8n4

    With newObj_k9m2
        .OutputPath_k9m2 = pvarOutputPath_k9m2x
        .Orientation_n7j3 = pvarOrientation_n7j3x
        .PaperSize_m8k4 = pvarPaperSize_m8k4x
        .FitToWidth_k3n9 = pvarFitToWidth_k3n9x
        .ScalePercent_m7n2 = pvarScalePercent_m7n2x
        .MarginLeft_k2n8 = pvarMarginLeft_k2n8x
        .MarginRight_n9k3 = pvarMarginRight_n9k3x
        .MarginTop_k8m9 = pvarMarginTop_k8m9x
        .MarginBottom_m3k7 = pvarMarginBottom_m3k7x
        .IncludeHeaders_n7k2 = pvarIncludeHeaders_n7k2x
        .PrintGridlines_k9m8 = pvarPrintGridlines_k9m8x
        .WrapLongText_m2n7 = pvarWrapLongText_m2n7x
        .HandleMergedCells_k8n3 = pvarHandleMergedCells_k8n3x
        .HighQuality_n4k9 = pvarHighQuality_n4k9x
    End With

    Set xpdf_Clone_m8k4 = newObj_k9m2
End Function
