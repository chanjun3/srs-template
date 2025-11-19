<#
.SYNOPSIS
  Restructures the legacy SRS folders into the normalized docs/ tree.

.NOTES
  Idempotent: running multiple times will skip work when sources are missing or
  destinations already contain the expected files.
#>

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Write-Task ($Message) {
  Write-Host "[srs] $Message"
}

function Ensure-Directory ($Path) {
  if (-not (Test-Path -LiteralPath $Path)) {
    Write-Task "Creating directory: $Path"
    New-Item -ItemType Directory -Path $Path | Out-Null
  }
}

function Safe-Move {
  param(
    [Parameter(Mandatory = $true)][string] $Source,
    [Parameter(Mandatory = $true)][string] $Destination
  )

  if (-not (Test-Path -LiteralPath $Source)) {
    return
  }
  $destDir = Split-Path -Parent $Destination
  if ($destDir) {
    Ensure-Directory -Path $destDir
  }
  if (Test-Path -LiteralPath $Destination) {
    Write-Task "Destination already exists, skipping move: $Destination"
    return
  }
  Write-Task "Moving '$Source' -> '$Destination'"
  Move-Item -LiteralPath $Source -Destination $Destination
}

$root = Resolve-Path (Join-Path $PSScriptRoot '..')
Set-Location $root

# Ensure baseline directories.
$docDirs = @(
  'docs',
  'docs\overview',
  'docs\governance',
  'docs\templates\3layer',
  'docs\requirements\functional',
  'docs\requirements\non-functional',
  'docs\requirements\integration',
  'docs\requirements\data',
  'docs\case-studies',
  'docs\case-studies\config',
  'docs\assurance'
)
$docDirs | ForEach-Object { Ensure-Directory -Path $_ }

# Overview files.
Safe-Move -Source '00_Overview\AI_Agent_NotionDB_Architecture_Requirements.md' -Destination 'docs\overview\AI_Agent_NotionDB_Architecture_Requirements.md'
Safe-Move -Source '00_Overview\AI_Cognitive_Framework_Report.md' -Destination 'docs\overview\AI_Cognitive_Framework_Report.md'
Safe-Move -Source '00_Overview\Branch_Management_Requirements.md' -Destination 'docs\governance\Branch_Management_Requirements.md'
Safe-Move -Source '00_Overview\Standard_CollectorAgent_Framework_Requirements.md' -Destination 'docs\case-studies\standard-collector\README.md'
Safe-Move -Source '00_Overview\architecture_overview_3layer.md' -Destination 'docs\templates\3layer\architecture_overview.md'

# Functional requirements + case studies.
$caseStudyMap = @{
  'AI_Cognitive_Loop_Requirements.md'        = 'cognitive-loop\README.md'
  'AI_Literacy_Development_System_SRS.md'    = 'assurance\AI_Literacy_Development_System_SRS.md'
  'CorporateActivityWatcherAgent_SRS.md'     = 'case-studies\corporate-activity-watcher\README.md'
  'IaC_Integration_SRS.md'                   = 'case-studies\iac-integration\README.md'
  'LogAnalyzerAgent_SRS.md'                  = 'case-studies\log-analyzer\README.md'
  'MacroSignal_Intelligence_SRS.md'          = 'case-studies\macrosignal-intelligence\README.md'
  'PlannerAgent_Qlearning_SRS.md'            = 'case-studies\planner-qlearning\README.md'
  'ReinforceTrainerAgent_SRS.md'             = 'case-studies\reinforce-trainer\README.md'
  'ValuationFeedbackAnalyzer_SRS.md'         = 'case-studies\valuation-feedback\README.md'
}
foreach ($entry in $caseStudyMap.GetEnumerator()) {
  $source = Join-Path '10_Functional_Requirements' $entry.Key
  $destination = Join-Path 'docs' $entry.Value
  Ensure-Directory -Path (Split-Path -Parent $destination)
  Safe-Move -Source $source -Destination $destination
}
Safe-Move -Source '10_Functional_Requirements\3layer_system_functional_requirements.md' -Destination 'docs\templates\3layer\functional_requirements.md'

# Shared configs.
$configSourceDir = '10_Functional_Requirements\config'
if (Test-Path -LiteralPath $configSourceDir) {
  Get-ChildItem -LiteralPath $configSourceDir -File | ForEach-Object {
    Safe-Move -Source $_.FullName -Destination (Join-Path 'docs\case-studies\config' $_.Name)
  }
}
Safe-Move -Source '10_Functional_Requirements\log_analyzer_config.yaml' -Destination 'docs\case-studies\config\log_analyzer_config.yaml'
Safe-Move -Source '10_Functional_Requirements\reward_config.yaml' -Destination 'docs\case-studies\config\reward_config.yaml'
Safe-Move -Source '10_Functional_Requirements\training_workflow.yaml' -Destination 'docs\case-studies\config\training_workflow.yaml'
Safe-Move -Source 'cognitive_loop.yaml' -Destination 'docs\case-studies\config\cognitive_loop.yaml'

# Non-functional / governance / integration / data moves.
Safe-Move -Source '20_NonFunctional_Requirements\3layer_nfr.md' -Destination 'docs\templates\3layer\non_functional_requirements.md'
Safe-Move -Source '20_NonFunctional_Requirements\cloud_native_deployment_strategy.md' -Destination 'docs\requirements\non-functional\cloud_native_deployment_strategy.md'
Safe-Move -Source '20_NonFunctional_Requirements\Data_Utilization_Policy_SRS.md' -Destination 'docs\governance\Data_Utilization_Policy_SRS.md'

Safe-Move -Source '30_Integration_Requirements\3layer_integration.md' -Destination 'docs\templates\3layer\integration_requirements.md'
Safe-Move -Source '30_Integration_Requirements\Serverless_Execution_Architecture.md' -Destination 'docs\requirements\integration\Serverless_Execution_Architecture.md'

Safe-Move -Source '40_Data_Requirements\3layer_data_schema.md' -Destination 'docs\templates\3layer\data_schema.md'
if (Test-Path -LiteralPath '40_Data_Requirements\40_05_CognitiveLoggingArchitecture.md') {
  $target = 'docs\requirements\data\CognitiveLoggingArchitecture.md'
  if (-not (Test-Path -LiteralPath $target)) {
    Safe-Move -Source '40_Data_Requirements\40_05_CognitiveLoggingArchitecture.md' -Destination $target
  } else {
    Remove-Item -LiteralPath '40_Data_Requirements\40_05_CognitiveLoggingArchitecture.md'
  }
}

Safe-Move -Source '50_Quality_Assurance\3layer_quality_assurance.md' -Destination 'docs\templates\3layer\quality_assurance.md'
Safe-Move -Source '50_Quality_Assurance\CI_CD_Pipeline_SRS.md' -Destination 'docs\assurance\CI_CD_Pipeline_SRS.md'

# Remove empty legacy directories.
@(
  '00_Overview',
  '10_Functional_Requirements',
  '20_NonFunctional_Requirements',
  '30_Integration_Requirements',
  '40_Data_Requirements',
  '50_Quality_Assurance'
) | ForEach-Object {
  if (Test-Path -LiteralPath $_) {
    $items = Get-ChildItem -LiteralPath $_ -Recurse -Force
    if (-not $items) {
      Remove-Item -LiteralPath $_ -Force
    }
  }
}

Write-Task "Restructure completed."
cmd /c "tree /F"
