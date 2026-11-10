package com.ghdinteractivestudio.aioffice.ui.navigation

sealed class Screen(val route: String, val title: String) {
    data object LiveOffice : Screen("live_office", "Live Office")
    data object VideoEngine : Screen("video_engine", "Video Engine")
    data object ProductionPipeline : Screen("production_pipeline", "Production")
    data object TalkToCeo : Screen("talk_to_ceo", "Talk to CEO")
    data object CeoOffice : Screen("ceo_office", "CEO Office")
    data object CeoDecisions : Screen("ceo_decisions", "CEO Decisions")
    data object CeoStrategy : Screen("ceo_strategy", "CEO Strategy")
    data object DepartmentActivity : Screen("department_activity", "Department Activity")
    data object AgentNetwork : Screen("agent_network", "Agent Network")
    data object TasksAndProgress : Screen("tasks_and_progress", "Tasks & Progress")
    data object PendingUserApprovals : Screen("pending_user_approvals", "Pending User Approvals")
    data object SocialAccounts : Screen("social_accounts", "Social Accounts")
    data object ExecutiveReports : Screen("executive_reports", "Executive Reports")
    data object OfficeCalendar : Screen("office_calendar", "Office Calendar")
    data object OrganizationalMemory : Screen("organizational_memory", "Organizational Memory")

    companion object {
        val allScreens: List<Screen>
            get() = listOf(
                LiveOffice,
                VideoEngine,
                ProductionPipeline,
                TalkToCeo,
                CeoOffice,
                CeoDecisions,
                CeoStrategy,
                DepartmentActivity,
                AgentNetwork,
                TasksAndProgress,
                PendingUserApprovals,
                SocialAccounts,
                ExecutiveReports,
                OfficeCalendar,
                OrganizationalMemory
            )
    }
}
