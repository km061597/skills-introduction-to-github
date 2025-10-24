VERSION 1.0 CLASS
BEGIN
  MultiUse = -1  'True
END
Attribute VB_Name = "xpdf_SheetAnalysisClass_k9n7"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = False
Attribute VB_Exposed = False
'===============================================================================
' DELIVERABLE 4A: Sheet Analysis Class Module
' Purpose: Stores comprehensive analysis data for a worksheet
' Instructions: Insert > Class Module, name it exactly as shown above, paste code
'===============================================================================

Option Explicit

' Private member variables
Private pvarSheetName_k9m2x As String
Private pvarRowCount_k8m3x As Long
Private pvarColumnCount_m7n2x As Long
Private pvarUsedRange_n9k4x As String
Private pvarHasHeaders_m9k2x As Boolean
Private pvarDataDensity_k3j8x As Double
Private pvarMergedCellCount_k7n3x As Long
Private pvarLongTextCellCount_n8m4x As Long
Private pvarMaxCellLength_k9j2x As Long
Private pvarHasWideColumns_m3k8x As Boolean
Private pvarEstimatedPages_k2n9x As Long
Private pvarRecommendedOrientation_n7k4x As String
Private pvarRequiresScaling_k8m9x As Boolean
Private pvarOptimalScale_m9n3x As Long

'===============================================================================
' PROPERTY: SheetName_k9m2
'===============================================================================

Public Property Get SheetName_k9m2() As String
    SheetName_k9m2 = pvarSheetName_k9m2x
End Property

Public Property Let SheetName_k9m2(ByVal vData As String)
    pvarSheetName_k9m2x = vData
End Property

'===============================================================================
' PROPERTY: RowCount_k8m3
'===============================================================================

Public Property Get RowCount_k8m3() As Long
    RowCount_k8m3 = pvarRowCount_k8m3x
End Property

Public Property Let RowCount_k8m3(ByVal vData As Long)
    pvarRowCount_k8m3x = vData
End Property

'===============================================================================
' PROPERTY: ColumnCount_m7n2
'===============================================================================

Public Property Get ColumnCount_m7n2() As Long
    ColumnCount_m7n2 = pvarColumnCount_m7n2x
End Property

Public Property Let ColumnCount_m7n2(ByVal vData As Long)
    pvarColumnCount_m7n2x = vData
End Property

'===============================================================================
' PROPERTY: UsedRange_n9k4
'===============================================================================

Public Property Get UsedRange_n9k4() As String
    UsedRange_n9k4 = pvarUsedRange_n9k4x
End Property

Public Property Let UsedRange_n9k4(ByVal vData As String)
    pvarUsedRange_n9k4x = vData
End Property

'===============================================================================
' PROPERTY: HasHeaders_m9k2
'===============================================================================

Public Property Get HasHeaders_m9k2() As Boolean
    HasHeaders_m9k2 = pvarHasHeaders_m9k2x
End Property

Public Property Let HasHeaders_m9k2(ByVal vData As Boolean)
    pvarHasHeaders_m9k2x = vData
End Property

'===============================================================================
' PROPERTY: DataDensity_k3j8
'===============================================================================

Public Property Get DataDensity_k3j8() As Double
    DataDensity_k3j8 = pvarDataDensity_k3j8x
End Property

Public Property Let DataDensity_k3j8(ByVal vData As Double)
    pvarDataDensity_k3j8x = vData
End Property

'===============================================================================
' PROPERTY: MergedCellCount_k7n3
'===============================================================================

Public Property Get MergedCellCount_k7n3() As Long
    MergedCellCount_k7n3 = pvarMergedCellCount_k7n3x
End Property

Public Property Let MergedCellCount_k7n3(ByVal vData As Long)
    pvarMergedCellCount_k7n3x = vData
End Property

'===============================================================================
' PROPERTY: LongTextCellCount_n8m4
'===============================================================================

Public Property Get LongTextCellCount_n8m4() As Long
    LongTextCellCount_n8m4 = pvarLongTextCellCount_n8m4x
End Property

Public Property Let LongTextCellCount_n8m4(ByVal vData As Long)
    pvarLongTextCellCount_n8m4x = vData
End Property

'===============================================================================
' PROPERTY: MaxCellLength_k9j2
'===============================================================================

Public Property Get MaxCellLength_k9j2() As Long
    MaxCellLength_k9j2 = pvarMaxCellLength_k9j2x
End Property

Public Property Let MaxCellLength_k9j2(ByVal vData As Long)
    pvarMaxCellLength_k9j2x = vData
End Property

'===============================================================================
' PROPERTY: HasWideColumns_m3k8
'===============================================================================

Public Property Get HasWideColumns_m3k8() As Boolean
    HasWideColumns_m3k8 = pvarHasWideColumns_m3k8x
End Property

Public Property Let HasWideColumns_m3k8(ByVal vData As Boolean)
    pvarHasWideColumns_m3k8x = vData
End Property

'===============================================================================
' PROPERTY: EstimatedPages_k2n9
'===============================================================================

Public Property Get EstimatedPages_k2n9() As Long
    EstimatedPages_k2n9 = pvarEstimatedPages_k2n9x
End Property

Public Property Let EstimatedPages_k2n9(ByVal vData As Long)
    pvarEstimatedPages_k2n9x = vData
End Property

'===============================================================================
' PROPERTY: RecommendedOrientation_n7k4
'===============================================================================

Public Property Get RecommendedOrientation_n7k4() As String
    RecommendedOrientation_n7k4 = pvarRecommendedOrientation_n7k4x
End Property

Public Property Let RecommendedOrientation_n7k4(ByVal vData As String)
    pvarRecommendedOrientation_n7k4x = vData
End Property

'===============================================================================
' PROPERTY: RequiresScaling_k8m9
'===============================================================================

Public Property Get RequiresScaling_k8m9() As Boolean
    RequiresScaling_k8m9 = pvarRequiresScaling_k8m9x
End Property

Public Property Let RequiresScaling_k8m9(ByVal vData As Boolean)
    pvarRequiresScaling_k8m9x = vData
End Property

'===============================================================================
' PROPERTY: OptimalScale_m9n3
'===============================================================================

Public Property Get OptimalScale_m9n3() As Long
    OptimalScale_m9n3 = pvarOptimalScale_m9n3x
End Property

Public Property Let OptimalScale_m9n3(ByVal vData As Long)
    pvarOptimalScale_m9n3x = vData
End Property

'===============================================================================
' CLASS INITIALIZATION
'===============================================================================

Private Sub Class_Initialize()
    pvarSheetName_k9m2x = ""
    pvarRowCount_k8m3x = 0
    pvarColumnCount_m7n2x = 0
    pvarUsedRange_n9k4x = ""
    pvarHasHeaders_m9k2x = False
    pvarDataDensity_k3j8x = 0
    pvarMergedCellCount_k7n3x = 0
    pvarLongTextCellCount_n8m4x = 0
    pvarMaxCellLength_k9j2x = 0
    pvarHasWideColumns_m3k8x = False
    pvarEstimatedPages_k2n9x = 0
    pvarRecommendedOrientation_n7k4x = "Portrait"
    pvarRequiresScaling_k8m9x = False
    pvarOptimalScale_m9n3x = 100
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

Public Function xpdf_GetSummaryText_k9m7() As String
    Dim summary_k8m3 As String

    summary_k8m3 = "Sheet: " & pvarSheetName_k9m2x & vbCrLf
    summary_k8m3 = summary_k8m3 & "Dimensions: " & pvarRowCount_k8m3x & " x " & pvarColumnCount_m7n2x & vbCrLf
    summary_k8m3 = summary_k8m3 & "Density: " & Format(pvarDataDensity_k3j8x, "0.0%") & vbCrLf
    summary_k8m3 = summary_k8m3 & "Recommendation: " & pvarRecommendedOrientation_n7k4x

    If pvarRequiresScaling_k8m9x Then
        summary_k8m3 = summary_k8m3 & ", Scale " & pvarOptimalScale_m9n3x & "%"
    End If

    xpdf_GetSummaryText_k9m7 = summary_k8m3
End Function

Public Function xpdf_Clone_m8k4() As xpdf_SheetAnalysisClass_k9n7
    Dim newObj_k9m2 As xpdf_SheetAnalysisClass_k9n7
    Set newObj_k9m2 = New xpdf_SheetAnalysisClass_k9n7

    With newObj_k9m2
        .SheetName_k9m2 = pvarSheetName_k9m2x
        .RowCount_k8m3 = pvarRowCount_k8m3x
        .ColumnCount_m7n2 = pvarColumnCount_m7n2x
        .UsedRange_n9k4 = pvarUsedRange_n9k4x
        .HasHeaders_m9k2 = pvarHasHeaders_m9k2x
        .DataDensity_k3j8 = pvarDataDensity_k3j8x
        .MergedCellCount_k7n3 = pvarMergedCellCount_k7n3x
        .LongTextCellCount_n8m4 = pvarLongTextCellCount_n8m4x
        .MaxCellLength_k9j2 = pvarMaxCellLength_k9j2x
        .HasWideColumns_m3k8 = pvarHasWideColumns_m3k8x
        .EstimatedPages_k2n9 = pvarEstimatedPages_k2n9x
        .RecommendedOrientation_n7k4 = pvarRecommendedOrientation_n7k4x
        .RequiresScaling_k8m9 = pvarRequiresScaling_k8m9x
        .OptimalScale_m9n3 = pvarOptimalScale_m9n3x
    End With

    Set xpdf_Clone_m8k4 = newObj_k9m2
End Function
