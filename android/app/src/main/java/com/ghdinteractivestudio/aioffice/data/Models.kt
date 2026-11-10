package com.ghdinteractivestudio.aioffice.data

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
data class OfficeMetrics(
    @SerialName("total_agents") val totalAgents: Int = 0,
    @SerialName("online_agents") val onlineAgents: Int = 0,
    @SerialName("idle_agents") val idleAgents: Int = 0,
    @SerialName("working_agents") val workingAgents: Int = 0,
    @SerialName("failed_agents") val failedAgents: Int = 0,
    @SerialName("active_tasks") val activeTasks: Int = 0,
    @SerialName("completed_tasks") val completedTasks: Int = 0,
    @SerialName("pending_approvals") val pendingApprovals: Int = 0,
    @SerialName("today_cost_usd") val todayCostUsd: Double = 0.0
)

@Serializable
data class DepartmentItem(
    val id: String,
    val name: String,
    @SerialName("director_name") val directorName: String,
    val mission: String,
    val status: String = "ACTIVE"
)

@Serializable
data class AgentItem(
    val id: String,
    val name: String,
    @SerialName("department_id") val departmentId: String,
    val role: String,
    @SerialName("hierarchy_level") val hierarchyLevel: String,
    val status: String,
    @SerialName("current_task_id") val currentTaskId: String? = null,
    @SerialName("current_model") val currentModel: String? = null,
    @SerialName("tokens_input") val tokensInput: Int = 0,
    @SerialName("tokens_output") val tokensOutput: Int = 0,
    @SerialName("last_activity") val lastActivity: String
)

@Serializable
data class TaskItem(
    val id: String,
    val title: String,
    val description: String? = null,
    @SerialName("department_id") val departmentId: String,
    @SerialName("assigned_agent_id") val assignedAgentId: String? = null,
    val status: String,
    val priority: String,
    @SerialName("progress_pct") val progressPct: Int = 0,
    val result: String? = null
)

@Serializable
data class ApprovalItem(
    val id: String,
    @SerialName("agent_id") val agentId: String,
    @SerialName("department_id") val departmentId: String,
    @SerialName("action_type") val actionType: String,
    val destination: String,
    val payload: String,
    @SerialName("payload_hash") val payloadHash: String,
    @SerialName("risk_level") val riskLevel: String,
    val cost: Double = 0.0,
    val status: String,
    @SerialName("decision_comment") val decisionComment: String? = null,
    @SerialName("expires_at") val expiresAt: String
)

@Serializable
data class OwnerChatReq(
    val message: String
)

@Serializable
data class OwnerChatResp(
    val reply: String,
    val decisions: List<String> = emptyList(),
    @SerialName("tasks_created") val tasksCreated: List<String> = emptyList(),
    val timestamp: String
)

@Serializable
data class AICEOProfile(
    val id: String = "ceo-001",
    val name: String = "Nova Prime (AI CEO)",
    val title: String = "AI CEO / Chief Executive Intelligence",
    val status: String = "IDLE",
    @SerialName("active_strategic_goals") val activeStrategicGoals: List<String> = emptyList(),
    @SerialName("total_autonomous_decisions") val totalAutonomousDecisions: Int = 0,
    @SerialName("departments_supervised") val departmentsSupervised: Int = 8,
    @SerialName("tokens_consumed") val tokensConsumed: Int = 0,
    @SerialName("executive_health") val executiveHealth: String = "OPTIMAL"
)

@Serializable
data class SocialAccountStatus(
    val platform: String,
    val status: String,
    @SerialName("account_id") val accountId: String? = null,
    val username: String? = null,
    val permissions: List<String> = emptyList(),
    val capabilities: List<String> = emptyList()
)

@Serializable
data class CeoDecisionItem(
    val id: Int,
    val timestamp: String,
    val decision: String
)

@Serializable
data class ReportItem(
    val id: String,
    @SerialName("report_type") val reportType: String,
    @SerialName("department_id") val departmentId: String,
    @SerialName("reporting_period") val reportingPeriod: String,
    val content: String,
    @SerialName("created_at") val createdAt: String
)

@Serializable
data class KnowledgeItem(
    val id: String,
    val title: String,
    val category: String,
    val content: String,
    val provenance: String = "system",
    @SerialName("created_at") val createdAt: String = ""
)

@Serializable
data class CalendarEventItem(
    val id: String,
    val title: String,
    @SerialName("schedule_time") val scheduleTime: String,
    val description: String,
    val status: String
)

// ─── Autonomous AI Media Company Models ──────────────────────────

@Serializable
data class EmployeeItem(
    val id: String,
    val name: String,
    val department: String,
    val role: String,
    val level: Int = 1,
    val xp: Int = 0,
    val status: String = "FREE",
    @SerialName("current_task") val currentTask: String? = null,
    @SerialName("current_project") val currentProject: String? = null,
    @SerialName("last_activity") val lastActivity: String? = null,
    @SerialName("session_id") val sessionId: String? = null,
    @SerialName("current_blockers") val currentBlockers: List<String> = emptyList()
)

@Serializable
data class WorkforceStats(
    val total: Int = 0,
    val working: Int = 0,
    val free: Int = 0,
    @SerialName("waiting_for_owner") val waitingForOwner: Int = 0,
    val stuck: Int = 0,
    val offline: Int = 0,
    @SerialName("by_department") val byDepartment: Map<String, Int> = emptyMap()
)

@Serializable
data class CompanyGovernance(
    @SerialName("human_role") val humanRole: String = "OWNER_PRINCIPAL",
    @SerialName("central_intelligence") val centralIntelligence: String = "AI Office (Nova Prime)"
)

@Serializable
data class CompanyOverview(
    @SerialName("company_name") val companyName: String = "AI Office Media Organization",
    val governance: CompanyGovernance = CompanyGovernance(),
    val workforce: WorkforceStats = WorkforceStats(),
    @SerialName("projects_count") val projectsCount: Int = 0,
    @SerialName("engine_state") val engineState: String = "UNKNOWN",
    val employees: List<EmployeeItem> = emptyList()
)

@Serializable
data class ProjectItem(
    val id: String,
    val title: String,
    val topic: String,
    val niche: String,
    @SerialName("target_audience") val targetAudience: String,
    val status: String,
    @SerialName("opportunity_score") val opportunityScore: Double = 8.0,
    @SerialName("confidence_pct") val confidencePct: Int = 85
)

@Serializable
data class FlowKitStatus(
    val state: String = "UNKNOWN",
    val endpoint: String = "http://127.0.0.1:8100",
    val port: Int = 8100,
    @SerialName("websocket_port") val websocketPort: Int = 9222,
    @SerialName("process_info") val processInfo: String? = null
)

@Serializable
data class GoogleAccountItem(
    val id: String,
    @SerialName("account_email_masked") val accountEmailMasked: String,
    @SerialName("auth_status") val authStatus: String,
    @SerialName("available_quota") val availableQuota: String = "UNKNOWN",
    @SerialName("current_usage") val currentUsage: String? = null,
    @SerialName("is_available") val isAvailable: Int = 0
)

@Serializable
data class LibraryProposalItem(
    val id: String,
    @SerialName("tool_name") val toolName: String,
    @SerialName("repository_url") val repositoryUrl: String,
    @SerialName("license_name") val licenseName: String,
    @SerialName("arm64_compatible") val arm64Compatible: Int = 1,
    @SerialName("proot_compatible") val prootCompatible: Int = 1,
    val benefits: String = "",
    val recommendation: String = "",
    val status: String = "IN_NEEDS_YOU",
    @SerialName("approval_id") val approvalId: String? = null
)

