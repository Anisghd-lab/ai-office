package com.ghdinteractivestudio.aioffice

import com.ghdinteractivestudio.aioffice.data.*
import com.ghdinteractivestudio.aioffice.ui.navigation.Screen
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import org.junit.Assert.*
import org.junit.Test

class OfficeModelsTest {

    private val json = Json {
        ignoreUnknownKeys = true
        isLenient = true
    }

    @Test
    fun testOfficeMetricsSerialization() {
        val rawJson = """
            {
                "total_agents": 9,
                "online_agents": 9,
                "idle_agents": 8,
                "working_agents": 1,
                "failed_agents": 0,
                "active_tasks": 3,
                "completed_tasks": 12,
                "pending_approvals": 1,
                "today_cost_usd": 0.0
            }
        """.trimIndent()

        val metrics = json.decodeFromString<OfficeMetrics>(rawJson)
        assertEquals(9, metrics.totalAgents)
        assertEquals(1, metrics.pendingApprovals)
        assertEquals(0.0, metrics.todayCostUsd, 0.0001)
    }

    @Test
    fun testOwnerChatResponseSerialization() {
        val rawJson = """
            {
                "reply": "I am directing the Research team to evaluate competitor metrics.",
                "decisions": ["Initiate market scan", "Review findings with Strategy"],
                "tasks_created": ["tsk-001", "tsk-002"],
                "timestamp": "2026-11-09T22:00:00Z"
            }
        """.trimIndent()

        val resp = json.decodeFromString<OwnerChatResp>(rawJson)
        assertTrue(resp.reply.contains("Research"))
        assertEquals(2, resp.decisions.size)
        assertEquals(2, resp.tasksCreated.size)
    }

    @Test
    fun testAICEOProfileDefaults() {
        val profile = AICEOProfile()
        assertEquals("ceo-001", profile.id)
        assertTrue(profile.name.contains("Nova Prime"))
        assertTrue(profile.name.contains("AI CEO"))
        assertEquals(8, profile.departmentsSupervised)
    }

    @Test
    fun testNavigationScreensCountAndRoutes() {
        // Assert all required sections exist (12 baseline + 3 media company screens)
        val screens = Screen.allScreens
        assertEquals(15, screens.size)

        for (screen in screens) {
            assertNotNull("Screen must not be null", screen)
            assertTrue("Screen title must not be blank", screen.title.isNotBlank())
            assertTrue("Screen route must not be blank", screen.route.isNotBlank())
        }

        val routes = screens.map { it.route }.toSet()
        assertTrue(routes.contains("talk_to_ceo"))
        assertTrue(routes.contains("ceo_office"))
        assertTrue(routes.contains("ceo_decisions"))
        assertTrue(routes.contains("ceo_strategy"))
        assertTrue(routes.contains("department_activity"))
        assertTrue(routes.contains("agent_network"))
        assertTrue(routes.contains("tasks_and_progress"))
        assertTrue(routes.contains("pending_user_approvals"))
        assertTrue(routes.contains("social_accounts"))
        assertTrue(routes.contains("executive_reports"))
        assertTrue(routes.contains("office_calendar"))
        assertTrue(routes.contains("organizational_memory"))
    }

    @Test
    fun testReportAndKnowledgeSerialization() {
        val reportJson = """
            {
                "id": "rep-001",
                "report_type": "DAILY_BRIEFING",
                "department_id": "operations",
                "reporting_period": "2026-11-10",
                "content": "All departments active",
                "created_at": "2026-11-10T08:00:00Z"
            }
        """.trimIndent()
        val report = json.decodeFromString<ReportItem>(reportJson)
        assertEquals("rep-001", report.id)
        assertEquals("DAILY_BRIEFING", report.reportType)

        val memoryJson = """
            {
                "id": "mem-001",
                "title": "Commercial Zero-Cost Invariant",
                "category": "finance",
                "content": "Zero paid APIs permitted",
                "provenance": "Finance Director",
                "created_at": "2026-11-10T08:00:00Z"
            }
        """.trimIndent()
        val mem = json.decodeFromString<KnowledgeItem>(memoryJson)
        assertEquals("mem-001", mem.id)
        assertEquals("finance", mem.category)
    }

    @Test
    fun testCalendarAndDecisionSerialization() {
        val calJson = """
            {
                "id": "cad-001",
                "title": "Daily Executive Briefing",
                "schedule_time": "Every Day at 08:00 (Africa/Algiers)",
                "description": "Nova Prime prepares briefing",
                "status": "ACTIVE_RECURRING"
            }
        """.trimIndent()
        val cal = json.decodeFromString<CalendarEventItem>(calJson)
        assertEquals("cad-001", cal.id)
        assertEquals("ACTIVE_RECURRING", cal.status)

        val decJson = """
            {
                "id": 42,
                "timestamp": "2026-11-10T09:00:00Z",
                "decision": "Delegated competitive scan to Research"
            }
        """.trimIndent()
        val dec = json.decodeFromString<CeoDecisionItem>(decJson)
        assertEquals(42, dec.id)
        assertEquals("Delegated competitive scan to Research", dec.decision)
    }

    @Test
    fun testMediaCompanyModelsSerialization() {
        val empJson = """
            {
                "id": "emp-res-01",
                "name": "Dr. Aris Vance",
                "department": "research",
                "role": "Research Director",
                "level": 8,
                "xp": 2100,
                "status": "FREE",
                "current_task": null,
                "current_project": null,
                "last_activity": "2026-11-10T11:45:00Z",
                "session_id": "ses-res-001",
                "current_blockers": []
            }
        """.trimIndent()
        val emp = json.decodeFromString<EmployeeItem>(empJson)
        assertEquals("emp-res-01", emp.id)
        assertEquals("Dr. Aris Vance", emp.name)
        assertEquals(8, emp.level)
        assertEquals(2100, emp.xp)
        assertEquals("FREE", emp.status)

        val flowkitJson = """
            {
                "state": "RUNNING",
                "endpoint": "http://127.0.0.1:8100",
                "port": 8100,
                "websocket_port": 9222,
                "process_info": "Process: RUNNING"
            }
        """.trimIndent()
        val fk = json.decodeFromString<FlowKitStatus>(flowkitJson)
        assertEquals("RUNNING", fk.state)
        assertEquals(8100, fk.port)

        val projJson = """
            {
                "id": "proj-ai-2026",
                "title": "Future of Autonomous Agents",
                "topic": "Autonomous AI Organizations",
                "niche": "Tech",
                "target_audience": "Developers",
                "status": "DISCOVERY",
                "opportunity_score": 9.2,
                "confidence_pct": 95
            }
        """.trimIndent()
        val proj = json.decodeFromString<ProjectItem>(projJson)
        assertEquals("proj-ai-2026", proj.id)
        assertEquals(9.2, proj.opportunityScore, 0.01)

        val gaccJson = """
            {
                "id": "gacc-01",
                "account_email_masked": "pro.account.1***@gmail.com",
                "auth_status": "AUTHENTICATED",
                "available_quota": "100 credits",
                "is_available": 1
            }
        """.trimIndent()
        val gacc = json.decodeFromString<GoogleAccountItem>(gaccJson)
        assertEquals("gacc-01", gacc.id)
        assertEquals(1, gacc.isAvailable)

        val libJson = """
            {
                "id": "lib-001",
                "tool_name": "remotion-cli",
                "repository_url": "https://github.com/remotion-dev/remotion",
                "license_name": "MIT",
                "arm64_compatible": 1,
                "proot_compatible": 1,
                "benefits": "Fast declarative video rendering",
                "recommendation": "PROCEED",
                "status": "IN_NEEDS_YOU"
            }
        """.trimIndent()
        val lib = json.decodeFromString<LibraryProposalItem>(libJson)
        assertEquals("remotion-cli", lib.toolName)
        assertEquals("IN_NEEDS_YOU", lib.status)
    }

    @Test
    fun testScreenNavigationItems() {
        val screens = Screen.allScreens
        assertTrue(screens.contains(Screen.LiveOffice))
        assertTrue(screens.contains(Screen.VideoEngine))
        assertTrue(screens.contains(Screen.ProductionPipeline))
        assertTrue(screens.contains(Screen.TalkToCeo))
        assertTrue(screens.contains(Screen.PendingUserApprovals))
        assertEquals(15, screens.size)
    }
}

