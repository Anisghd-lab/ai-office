package com.ghdinteractivestudio.aioffice.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.ghdinteractivestudio.aioffice.data.AICEOProfile
import com.ghdinteractivestudio.aioffice.data.AgentItem
import com.ghdinteractivestudio.aioffice.data.ApiClient
import com.ghdinteractivestudio.aioffice.data.ApprovalItem
import com.ghdinteractivestudio.aioffice.data.DepartmentItem
import com.ghdinteractivestudio.aioffice.data.OfficeMetrics
import com.ghdinteractivestudio.aioffice.data.SocialAccountStatus
import com.ghdinteractivestudio.aioffice.data.SseClient
import com.ghdinteractivestudio.aioffice.data.TaskItem
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
                _connectionState.value = "CONNECTED"
            } catch (e: Exception) {
                _connectionState.value = "OFFLINE"
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
