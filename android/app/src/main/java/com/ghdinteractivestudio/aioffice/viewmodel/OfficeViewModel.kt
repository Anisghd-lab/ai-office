package com.ghdinteractivestudio.aioffice.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.ghdinteractivestudio.aioffice.data.AICEOProfile
import com.ghdinteractivestudio.aioffice.data.AgentItem
import com.ghdinteractivestudio.aioffice.data.ApiClient
import com.ghdinteractivestudio.aioffice.data.ApprovalItem
import com.ghdinteractivestudio.aioffice.data.CalendarEventItem
import com.ghdinteractivestudio.aioffice.data.CeoDecisionItem
import com.ghdinteractivestudio.aioffice.data.DepartmentItem
import com.ghdinteractivestudio.aioffice.data.KnowledgeItem
import com.ghdinteractivestudio.aioffice.data.OfficeMetrics
import com.ghdinteractivestudio.aioffice.data.ReportItem
import com.ghdinteractivestudio.aioffice.data.SocialAccountStatus
import com.ghdinteractivestudio.aioffice.data.SseClient
import com.ghdinteractivestudio.aioffice.data.TaskItem
import com.ghdinteractivestudio.aioffice.data.CompanyOverview
import com.ghdinteractivestudio.aioffice.data.EmployeeItem
import com.ghdinteractivestudio.aioffice.data.FlowKitStatus
import com.ghdinteractivestudio.aioffice.data.ProjectItem
import com.ghdinteractivestudio.aioffice.data.GoogleAccountItem
import com.ghdinteractivestudio.aioffice.data.LibraryProposalItem
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

data class ChatMessage(
    val sender: String, // "USER" or "AI_CEO"
    val text: String,
    val timestamp: String,
    val decisions: List<String> = emptyList()
)

class OfficeViewModel(
    private val api: ApiClient = ApiClient(),
    private val sse: SseClient = SseClient()
) : ViewModel() {

    private val _metrics = MutableStateFlow(OfficeMetrics())
    val metrics: StateFlow<OfficeMetrics> = _metrics.asStateFlow()

    private val _departments = MutableStateFlow<List<DepartmentItem>>(emptyList())
    val departments: StateFlow<List<DepartmentItem>> = _departments.asStateFlow()

    private val _agents = MutableStateFlow<List<AgentItem>>(emptyList())
    val agents: StateFlow<List<AgentItem>> = _agents.asStateFlow()

    private val _tasks = MutableStateFlow<List<TaskItem>>(emptyList())
    val tasks: StateFlow<List<TaskItem>> = _tasks.asStateFlow()

    private val _approvals = MutableStateFlow<List<ApprovalItem>>(emptyList())
    val approvals: StateFlow<List<ApprovalItem>> = _approvals.asStateFlow()

    private val _socialAccounts = MutableStateFlow<Map<String, SocialAccountStatus>>(emptyMap())
    val socialAccounts: StateFlow<Map<String, SocialAccountStatus>> = _socialAccounts.asStateFlow()

    private val _ceoProfile = MutableStateFlow(AICEOProfile())
    val ceoProfile: StateFlow<AICEOProfile> = _ceoProfile.asStateFlow()

    private val _decisions = MutableStateFlow<List<CeoDecisionItem>>(emptyList())
    val decisions: StateFlow<List<CeoDecisionItem>> = _decisions.asStateFlow()

    private val _reports = MutableStateFlow<List<ReportItem>>(emptyList())
    val reports: StateFlow<List<ReportItem>> = _reports.asStateFlow()

    private val _memory = MutableStateFlow<List<KnowledgeItem>>(emptyList())
    val memory: StateFlow<List<KnowledgeItem>> = _memory.asStateFlow()

    private val _calendar = MutableStateFlow<List<CalendarEventItem>>(emptyList())
    val calendar: StateFlow<List<CalendarEventItem>> = _calendar.asStateFlow()

    // ─── Media Company State ──────────────────────────────────────
    private val _companyOverview = MutableStateFlow(CompanyOverview())
    val companyOverview: StateFlow<CompanyOverview> = _companyOverview.asStateFlow()

    private val _employees = MutableStateFlow<List<EmployeeItem>>(emptyList())
    val employees: StateFlow<List<EmployeeItem>> = _employees.asStateFlow()

    private val _flowkitStatus = MutableStateFlow(FlowKitStatus())
    val flowkitStatus: StateFlow<FlowKitStatus> = _flowkitStatus.asStateFlow()

    private val _flowkitLogs = MutableStateFlow("")
    val flowkitLogs: StateFlow<String> = _flowkitLogs.asStateFlow()

    private val _companyProjects = MutableStateFlow<List<ProjectItem>>(emptyList())
    val companyProjects: StateFlow<List<ProjectItem>> = _companyProjects.asStateFlow()

    private val _googleAccounts = MutableStateFlow<List<GoogleAccountItem>>(emptyList())
    val googleAccounts: StateFlow<List<GoogleAccountItem>> = _googleAccounts.asStateFlow()

    private val _libraryProposals = MutableStateFlow<List<LibraryProposalItem>>(emptyList())
    val libraryProposals: StateFlow<List<LibraryProposalItem>> = _libraryProposals.asStateFlow()

    private val _chatMessages = MutableStateFlow<List<ChatMessage>>(
        listOf(
            ChatMessage(
                sender = "AI_CEO",
                text = "Welcome, Principal. I am Nova Prime, your AI CEO. I am actively directing our 8 departments. What strategic objective shall we address today?",
                timestamp = "Just now"
            )
        )
    )
    val chatMessages: StateFlow<List<ChatMessage>> = _chatMessages.asStateFlow()

    private val _connectionState = MutableStateFlow("CONNECTED")
    val connectionState: StateFlow<String> = _connectionState.asStateFlow()

    init {
        refreshAll()
        listenToSseTelemetry()
    }

    fun refreshAll() {
        viewModelScope.launch {
            try {
                _metrics.value = api.getMetrics()
                _departments.value = api.getDepartments()
                _agents.value = api.getAgents()
                _tasks.value = api.getTasks()
                _approvals.value = api.getApprovals("PENDING")
                _socialAccounts.value = api.getSocialAccounts()
                _ceoProfile.value = api.getCeoProfile()
                _decisions.value = api.getDecisions()
                _reports.value = api.getReports()
                _memory.value = api.getMemory()
                _calendar.value = api.getCalendar()
                refreshMediaCompany()
                _connectionState.value = "CONNECTED"
            } catch (e: Exception) {
                _connectionState.value = "OFFLINE"
            }
        }
    }

    fun refreshMediaCompany() {
        viewModelScope.launch {
            try {
                _companyOverview.value = api.getCompanyOverview()
                _employees.value = api.getEmployees()
                _flowkitStatus.value = api.getFlowKitStatus()
                _flowkitLogs.value = api.getFlowKitLogs()
                _companyProjects.value = api.getCompanyProjects()
                _googleAccounts.value = api.getGoogleAccounts()
                _libraryProposals.value = api.getLibraryProposals()
            } catch (e: Exception) {
                // Keep resilient defaults
            }
        }
    }

    fun controlFlowKitEngine(action: String) {
        viewModelScope.launch {
            try {
                api.controlFlowKit(action)
                _flowkitStatus.value = api.getFlowKitStatus()
                _flowkitLogs.value = api.getFlowKitLogs()
            } catch (e: Exception) {
                // Keep resilient
            }
        }
    }

    private fun listenToSseTelemetry() {
        viewModelScope.launch {
            sse.observeEvents().collect { msg ->
                when (msg.event) {
                    "disconnected" -> _connectionState.value = "RECONNECTING"
                    "task.created", "task.assigned", "task.completed" -> {
                        _tasks.value = api.getTasks()
                        _metrics.value = api.getMetrics()
                    }
                    "approval.created", "approval.approved", "approval.rejected" -> {
                        _approvals.value = api.getApprovals("PENDING")
                        _metrics.value = api.getMetrics()
                    }
                    "agent.started", "agent.paused", "agent.resumed" -> {
                        _agents.value = api.getAgents()
                    }
                    "employee.session_started", "employee.session_finished", "employee.xp_awarded",
                    "production.job_updated", "library.proposal_created" -> {
                        refreshMediaCompany()
                    }
                    "connected" -> _connectionState.value = "LIVE"
                }
            }
        }
    }

    fun sendUserMessageToCeo(messageText: String) {
        if (messageText.isBlank()) return
        val userMsg = ChatMessage(sender = "USER", text = messageText, timestamp = "Now")
        _chatMessages.value = _chatMessages.value + userMsg

        viewModelScope.launch {
            try {
                val resp = api.chatWithCeo(messageText)
                val ceoMsg = ChatMessage(
                    sender = "AI_CEO",
                    text = resp.reply,
                    timestamp = "Now",
                    decisions = resp.decisions
                )
                _chatMessages.value = _chatMessages.value + ceoMsg
                _tasks.value = api.getTasks()
                _metrics.value = api.getMetrics()
            } catch (e: Exception) {
                _chatMessages.value = _chatMessages.value + ChatMessage(
                    sender = "AI_CEO",
                    text = "Executive communication error: ${e.message}",
                    timestamp = "Now"
                )
            }
        }
    }

    fun approvePendingAction(requestId: String) {
        viewModelScope.launch {
            try {
                api.approveRequest(requestId)
                _approvals.value = api.getApprovals("PENDING")
                _metrics.value = api.getMetrics()
            } catch (e: Exception) {
                // handle error
            }
        }
    }

    fun rejectPendingAction(requestId: String, reason: String) {
        viewModelScope.launch {
            try {
                api.rejectRequest(requestId, reason)
                _approvals.value = api.getApprovals("PENDING")
                _metrics.value = api.getMetrics()
            } catch (e: Exception) {
                // handle error
            }
        }
    }

    fun createNewTask(title: String, departmentId: String, priority: String, description: String?) {
        viewModelScope.launch {
            try {
                api.createTask(title, departmentId, priority, description)
                _tasks.value = api.getTasks()
                _metrics.value = api.getMetrics()
            } catch (e: Exception) {
                // handle error
            }
        }
    }
}
