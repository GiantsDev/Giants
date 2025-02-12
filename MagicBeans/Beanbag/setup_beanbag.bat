@echo off
setlocal enabledelayedexpansion

:: Set the base directory
set BASE_DIR=C:\Users\paulc\Giants\Github\GiantsDev\Giants\MagicBeans\Beanbag

:: Ensure base directory exists
if not exist "%BASE_DIR%" mkdir "%BASE_DIR%"

:: List of Magic Beans
for %%B in (
    CoreArithmeticBean
    EquationValidationBean
    SelfIdentityBean
    CrossModelClarityBean
    IterativeReasoningBean
    ConfidenceScoringBean
    HolisticConfidenceMatrixBean
    ToolIntegrationBean
    ErrorDetectionBean
    AdaptiveEvolutionBean
    MemoryPersistenceBean
    ComparativeAnalysisBean
    HeuristicsBean
    UserGuidanceBean
    SyntaxParserBean
    MultiModalSupportBean
    IncrementalRefinementBean
    AutoDebugBean
    ValidationBean
    SummarizationBean
) do (
    set "BEAN_DIR=%BASE_DIR%\%%B"
    mkdir "!BEAN_DIR!"
    
    echo # %%B > "!BEAN_DIR!\README.md"
    echo # Purpose: Placeholder for %%B >> "!BEAN_DIR!\README.md"
    echo. >> "!BEAN_DIR!\README.md"
    echo # Description: [To be completed] >> "!BEAN_DIR!\README.md"
    
    echo # Placeholder script for %%B > "!BEAN_DIR!\script.py"
    echo # This script will be filled out for %%B later. >> "!BEAN_DIR!\script.py"
)

echo Done! Your Magic Beans folders are ready in %BASE_DIR%
exit
