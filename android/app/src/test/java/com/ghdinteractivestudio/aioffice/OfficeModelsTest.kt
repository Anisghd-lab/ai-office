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
        // Assert all 12 required sections exist
        val screens = Screen.allScreens
        assertEquals(12, screens.size)

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
}

