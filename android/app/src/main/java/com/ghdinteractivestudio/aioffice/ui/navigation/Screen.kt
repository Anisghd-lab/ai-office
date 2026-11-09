package com.ghdinteractivestudio.aioffice.ui.navigation

sealed class Screen(val route: String, val title: String) {
    object TalkToCeo : Screen("talk_to_ceo", "Talk to CEO")
    object CeoOffice : Screen("ceo_office", "CEO Office")
    object CeoDecisions : Screen("ceo_decisions", "CEO Decisions")
    object CeoStrategy : Screen("ceo_strategy", "CEO Strategy")
    object DepartmentActivity : Screen("department_activity", "Department Activity")
    object AgentNetwork : Screen("agent_network", "Agent Network")
    object TasksAndProgress : Screen("tasks_and_progress", "Tasks & Progress")
    object PendingUserApprovals : Screen("pending_user_approvals", "Pending User Approvals")
    object SocialAccounts : Screen("social_accounts", "Social Accounts")
    object ExecutiveReports : Screen("executive_reports", "Executive Reports")
    object OfficeCalendar : Screen("office_calendar", "Office Calendar")
    object OrganizationalMemory : Screen("organizational_memory", "Organizational Memory")

    companion object {
        val allScreens = listOf(
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
