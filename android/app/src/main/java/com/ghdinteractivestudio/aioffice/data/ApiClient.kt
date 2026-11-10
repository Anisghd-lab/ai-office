package com.ghdinteractivestudio.aioffice.data

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import java.io.IOException
import java.util.concurrent.TimeUnit

class ApiClient(
    private val baseUrl: String = "http://127.0.0.1:8000/api/v1",
    private val ownerKey: String = "owner-default-dev-token"
) {
    private val client = OkHttpClient.Builder()
        .connectTimeout(5, TimeUnit.SECONDS)
        .readTimeout(15, TimeUnit.SECONDS)
        .build()

    private val json = Json {
        ignoreUnknownKeys = true
        isLenient = true
        encodeDefaults = true
    }

    private val jsonMediaType = "application/json; charset=utf-8".toMediaType()

    private fun requestBuilder(endpoint: String): Request.Builder {
        return Request.Builder()
            .url("$baseUrl$endpoint")
            .addHeader("X-Owner-Key", ownerKey)
            .addHeader("Accept", "application/json")
    }

    suspend fun getMetrics(): OfficeMetrics = withContext(Dispatchers.IO) {
        val req = requestBuilder("/metrics").get().build()
        client.newCall(req).execute().use { resp ->
            if (!resp.isSuccessful) throw IOException("Failed to load metrics: HTTP ${resp.code}")
            val body = resp.body?.string() ?: "{}"
            json.decodeFromString<OfficeMetrics>(body)
        }
    }

    suspend fun getDepartments(): List<DepartmentItem> = withContext(Dispatchers.IO) {
        val req = requestBuilder("/departments").get().build()
        client.newCall(req).execute().use { resp ->
            if (!resp.isSuccessful) throw IOException("Failed to load departments: HTTP ${resp.code}")
            val body = resp.body?.string() ?: "[]"
            json.decodeFromString<List<DepartmentItem>>(body)
        }
    }

    suspend fun getAgents(): List<AgentItem> = withContext(Dispatchers.IO) {
        val req = requestBuilder("/agents").get().build()
        client.newCall(req).execute().use { resp ->
            if (!resp.isSuccessful) throw IOException("Failed to load agents: HTTP ${resp.code}")
            val body = resp.body?.string() ?: "[]"
            json.decodeFromString<List<AgentItem>>(body)
        }
    }

    suspend fun getTasks(): List<TaskItem> = withContext(Dispatchers.IO) {
        val req = requestBuilder("/tasks").get().build()
        client.newCall(req).execute().use { resp ->
            if (!resp.isSuccessful) throw IOException("Failed to load tasks: HTTP ${resp.code}")
            val body = resp.body?.string() ?: "[]"
            json.decodeFromString<List<TaskItem>>(body)
        }
    }

    suspend fun createTask(title: String, departmentId: String, priority: String, description: String?): TaskItem = withContext(Dispatchers.IO) {
        val payload = """{"title":"$title","department_id":"$departmentId","priority":"$priority","description":"${description ?: ""}"}"""
        val req = requestBuilder("/tasks").post(payload.toRequestBody(jsonMediaType)).build()
        client.newCall(req).execute().use { resp ->
            if (!resp.isSuccessful) throw IOException("Failed to create task: HTTP ${resp.code}")
            val body = resp.body?.string() ?: "{}"
            json.decodeFromString<TaskItem>(body)
        }
    }

    suspend fun getApprovals(status: String? = null): List<ApprovalItem> = withContext(Dispatchers.IO) {
        val endpoint = if (status != null) "/governance/approvals?status_filter=$status" else "/governance/approvals"
        val req = requestBuilder(endpoint).get().build()
        client.newCall(req).execute().use { resp ->
            if (!resp.isSuccessful) throw IOException("Failed to load approvals: HTTP ${resp.code}")
            val body = resp.body?.string() ?: "[]"
            json.decodeFromString<List<ApprovalItem>>(body)
        }
    }

    suspend fun approveRequest(requestId: String, comment: String? = null): Boolean = withContext(Dispatchers.IO) {
        val payload = """{"decision":"APPROVED","comment":"${comment ?: "Approved by Human Owner"}"}"""
        val req = requestBuilder("/governance/approvals/$requestId/approve").post(payload.toRequestBody(jsonMediaType)).build()
        client.newCall(req).execute().use { resp -> resp.isSuccessful }
    }

    suspend fun rejectRequest(requestId: String, reason: String): Boolean = withContext(Dispatchers.IO) {
        val payload = """{"decision":"REJECTED","comment":"$reason"}"""
        val req = requestBuilder("/governance/approvals/$requestId/reject").post(payload.toRequestBody(jsonMediaType)).build()
        client.newCall(req).execute().use { resp -> resp.isSuccessful }
    }

    suspend fun chatWithCeo(message: String): OwnerChatResp = withContext(Dispatchers.IO) {
        val payload = json.encodeToString(OwnerChatReq(message = message))
        val req = requestBuilder("/ceo/chat").post(payload.toRequestBody(jsonMediaType)).build()
        client.newCall(req).execute().use { resp ->
            if (!resp.isSuccessful) throw IOException("Failed to communicate with AI CEO: HTTP ${resp.code}")
            val body = resp.body?.string() ?: "{}"
            json.decodeFromString<OwnerChatResp>(body)
        }
    }

    suspend fun getCeoProfile(): AICEOProfile = withContext(Dispatchers.IO) {
        val req = requestBuilder("/ceo/profile").get().build()
        client.newCall(req).execute().use { resp ->
            if (!resp.isSuccessful) return@use AICEOProfile()
            val body = resp.body?.string() ?: "{}"
            json.decodeFromString<AICEOProfile>(body)
        }
    }

    suspend fun getSocialAccounts(): Map<String, SocialAccountStatus> = withContext(Dispatchers.IO) {
        val req = requestBuilder("/social/accounts").get().build()
        client.newCall(req).execute().use { resp ->
            if (!resp.isSuccessful) throw IOException("Failed to load social accounts: HTTP ${resp.code}")
            val body = resp.body?.string() ?: "{}"
            json.decodeFromString<Map<String, SocialAccountStatus>>(body)
        }
    }

    suspend fun getDecisions(): List<CeoDecisionItem> = withContext(Dispatchers.IO) {
        val req = requestBuilder("/ceo/decisions").get().build()
        client.newCall(req).execute().use { resp ->
            if (!resp.isSuccessful) return@use emptyList()
            val body = resp.body?.string() ?: "[]"
            json.decodeFromString<List<CeoDecisionItem>>(body)
        }
    }

    suspend fun getReports(): List<ReportItem> = withContext(Dispatchers.IO) {
        val req = requestBuilder("/ceo/reports").get().build()
        client.newCall(req).execute().use { resp ->
            if (!resp.isSuccessful) return@use emptyList()
            val body = resp.body?.string() ?: "[]"
            json.decodeFromString<List<ReportItem>>(body)
        }
    }

    suspend fun getMemory(): List<KnowledgeItem> = withContext(Dispatchers.IO) {
        val req = requestBuilder("/ceo/memory").get().build()
        client.newCall(req).execute().use { resp ->
            if (!resp.isSuccessful) return@use emptyList()
            val body = resp.body?.string() ?: "[]"
            json.decodeFromString<List<KnowledgeItem>>(body)
        }
    }

    suspend fun getCalendar(): List<CalendarEventItem> = withContext(Dispatchers.IO) {
        val req = requestBuilder("/ceo/calendar").get().build()
        client.newCall(req).execute().use { resp ->
            if (!resp.isSuccessful) return@use emptyList()
            val body = resp.body?.string() ?: "[]"
            json.decodeFromString<List<CalendarEventItem>>(body)
        }
    }

    // ─── Autonomous AI Media Company API Methods ──────────────────

    suspend fun getCompanyOverview(): CompanyOverview = withContext(Dispatchers.IO) {
        val req = requestBuilder("/company/overview").get().build()
        client.newCall(req).execute().use { resp ->
            if (!resp.isSuccessful) return@use CompanyOverview()
            val body = resp.body?.string() ?: "{}"
            json.decodeFromString<CompanyOverview>(body)
        }
    }

    suspend fun getEmployees(): List<EmployeeItem> = withContext(Dispatchers.IO) {
        val req = requestBuilder("/company/employees").get().build()
        client.newCall(req).execute().use { resp ->
            if (!resp.isSuccessful) return@use emptyList()
            val body = resp.body?.string() ?: "[]"
            json.decodeFromString<List<EmployeeItem>>(body)
        }
    }

    suspend fun getFlowKitStatus(): FlowKitStatus = withContext(Dispatchers.IO) {
        val req = requestBuilder("/company/flowkit/status").get().build()
        client.newCall(req).execute().use { resp ->
            if (!resp.isSuccessful) return@use FlowKitStatus(state = "OFFLINE")
            val body = resp.body?.string() ?: "{}"
            json.decodeFromString<FlowKitStatus>(body)
        }
    }

    suspend fun controlFlowKit(action: String): Boolean = withContext(Dispatchers.IO) {
        val req = requestBuilder("/company/flowkit/control/$action").post("{}".toRequestBody(jsonMediaType)).build()
        client.newCall(req).execute().use { resp ->
            resp.isSuccessful
        }
    }

    suspend fun getFlowKitLogs(): String = withContext(Dispatchers.IO) {
        val req = requestBuilder("/company/flowkit/logs").get().build()
        client.newCall(req).execute().use { resp ->
            if (!resp.isSuccessful) return@use "No logs available or engine stopped."
            val body = resp.body?.string() ?: "{}"
            try {
                val parsed = json.decodeFromString<Map<String, String>>(body)
                parsed["logs"] ?: body
            } catch (e: Exception) {
                body
            }
        }
    }

    suspend fun getCompanyProjects(): List<ProjectItem> = withContext(Dispatchers.IO) {
        val req = requestBuilder("/company/projects").get().build()
        client.newCall(req).execute().use { resp ->
            if (!resp.isSuccessful) return@use emptyList()
            val body = resp.body?.string() ?: "[]"
            json.decodeFromString<List<ProjectItem>>(body)
        }
    }

    suspend fun getGoogleAccounts(): List<GoogleAccountItem> = withContext(Dispatchers.IO) {
        val req = requestBuilder("/company/accounts").get().build()
        client.newCall(req).execute().use { resp ->
            if (!resp.isSuccessful) return@use emptyList()
            val body = resp.body?.string() ?: "[]"
            json.decodeFromString<List<GoogleAccountItem>>(body)
        }
    }

    suspend fun getLibraryProposals(): List<LibraryProposalItem> = withContext(Dispatchers.IO) {
        val req = requestBuilder("/company/library/proposals").get().build()
        client.newCall(req).execute().use { resp ->
            if (!resp.isSuccessful) return@use emptyList()
            val body = resp.body?.string() ?: "[]"
            json.decodeFromString<List<LibraryProposalItem>>(body)
        }
    }
}

