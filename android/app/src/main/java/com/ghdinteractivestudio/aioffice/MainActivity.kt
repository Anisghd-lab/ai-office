package com.ghdinteractivestudio.aioffice

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.viewModels
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.ghdinteractivestudio.aioffice.ui.components.GlassCard
import com.ghdinteractivestudio.aioffice.ui.navigation.Screen
import com.ghdinteractivestudio.aioffice.ui.screens.*
import com.ghdinteractivestudio.aioffice.ui.theme.*
import com.ghdinteractivestudio.aioffice.viewmodel.OfficeViewModel

class MainActivity : ComponentActivity() {

    private val officeViewModel: OfficeViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            AIOfficeTheme {
                MainScreen(viewModel = officeViewModel)
            }
        }
    }
}

@Composable
fun MainScreen(viewModel: OfficeViewModel) {
    var currentScreen by remember { mutableStateOf<Screen>(Screen.TalkToCeo) }
    val connectionState by viewModel.connectionState.collectAsState()

    Scaffold(
        containerColor = DeepBlackBg,
        topBar = {
            TopAppBarGlass(
                currentScreen = currentScreen,
                connectionState = connectionState,
                onRefresh = { viewModel.refreshAll() }
            )
        },
        bottomBar = {
            NavigationBarGlass(
                currentScreen = currentScreen,
                onScreenSelected = { currentScreen = it }
            )
        }
    ) { paddingValues ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
        ) {
            when (currentScreen) {
                Screen.LiveOffice -> LiveOfficeBoardScreen(viewModel)
                Screen.VideoEngine -> VideoEngineControlScreen(viewModel)
                Screen.ProductionPipeline -> ProductionPipelineScreen(viewModel, onNavigateToApprovals = { currentScreen = Screen.PendingUserApprovals })
                Screen.TalkToCeo -> TalkToCeoScreen(viewModel)
                Screen.CeoOffice -> CeoOfficeScreen(viewModel)
                Screen.CeoDecisions -> CeoDecisionsScreen(viewModel)
                Screen.CeoStrategy -> CeoStrategyScreen(viewModel)
                Screen.DepartmentActivity -> DepartmentActivityScreen(viewModel)
                Screen.AgentNetwork -> AgentNetworkScreen(viewModel)
                Screen.TasksAndProgress -> TasksAndProgressScreen(viewModel)
                Screen.PendingUserApprovals -> PendingUserApprovalsScreen(viewModel)
                Screen.SocialAccounts -> SocialAccountsScreen(viewModel)
                Screen.ExecutiveReports -> ExecutiveReportsScreen(viewModel)
                Screen.OfficeCalendar -> OfficeCalendarScreen(viewModel)
                Screen.OrganizationalMemory -> OrganizationalMemoryScreen(viewModel)
            }
        }
    }
}

@Composable
fun TopAppBarGlass(
    currentScreen: Screen,
    connectionState: String,
    onRefresh: () -> Unit
) {
    GlassCard(
        modifier = Modifier
            .fillMaxWidth()
            .statusBarsPadding()
            .padding(horizontal = 12.dp, vertical = 6.dp),
        cornerRadius = 16.dp
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column {
                Text(
                    text = "AI OFFICE",
                    color = NeonCyan,
                    fontSize = 11.sp,
                    fontWeight = FontWeight.Bold,
                    letterSpacing = 1.sp
                )
                Text(
                    text = currentScreen.title,
                    color = TextPrimary,
                    fontSize = 17.sp,
                    fontWeight = FontWeight.Bold
                )
            }

            Row(verticalAlignment = Alignment.CenterVertically) {
                Box(
                    modifier = Modifier
                        .size(8.dp)
                        .clip(CircleShape)
                        .background(
                            when (connectionState) {
                                "CONNECTED", "LIVE" -> NeonEmerald
                                "RECONNECTING" -> NeonAmber
                                else -> NeonRose
                            }
                        )
                )
                Spacer(modifier = Modifier.width(6.dp))
                Text(
                    text = connectionState,
                    color = TextSecondary,
                    fontSize = 10.sp,
                    fontWeight = FontWeight.SemiBold
                )
            }
        }
    }
}

@Composable
fun NavigationBarGlass(
    currentScreen: Screen,
    onScreenSelected: (Screen) -> Unit
) {
    GlassCard(
        modifier = Modifier
            .fillMaxWidth()
            .navigationBarsPadding()
            .padding(horizontal = 8.dp, vertical = 4.dp),
        cornerRadius = 20.dp
    ) {
        LazyRow(
            horizontalArrangement = Arrangement.spacedBy(8.dp),
            verticalAlignment = Alignment.CenterVertically,
            modifier = Modifier.fillMaxWidth()
        ) {
            items(Screen.allScreens.filterNotNull()) { screen ->
                val isSelected = screen == currentScreen
                Box(
                    modifier = Modifier
                        .clip(RoundedCornerShape(12.dp))
                        .background(if (isSelected) NeonCyan.copy(alpha = 0.2f) else Color.Transparent)
                        .clickable { onScreenSelected(screen) }
                        .padding(horizontal = 12.dp, vertical = 8.dp)
                ) {
                    Text(
                        text = screen.title,
                        color = if (isSelected) NeonCyan else TextSecondary,
                        fontSize = 12.sp,
                        fontWeight = if (isSelected) FontWeight.Bold else FontWeight.Normal
                    )
                }
            }
        }
    }
}
