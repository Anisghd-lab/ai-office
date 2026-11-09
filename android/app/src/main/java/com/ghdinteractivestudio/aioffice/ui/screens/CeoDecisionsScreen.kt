package com.ghdinteractivestudio.aioffice.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.ghdinteractivestudio.aioffice.ui.components.GlassCard
import com.ghdinteractivestudio.aioffice.ui.theme.*
import com.ghdinteractivestudio.aioffice.viewmodel.OfficeViewModel

@Composable
fun CeoDecisionsScreen(viewModel: OfficeViewModel) {
    val ceoProfile by viewModel.ceoProfile.collectAsState()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        Text(
            text = "AI CEO AUTONOMOUS DECISIONS",
            color = NeonCyan,
            fontSize = 20.sp,
            fontWeight = FontWeight.Bold
        )
        Text(
            text = "Internal operational decisions made autonomously without bothering the Owner for trivial steps.",
            color = TextSecondary,
            fontSize = 12.sp
        )

        Spacer(modifier = Modifier.height(16.dp))

        LazyColumn(
            verticalArrangement = Arrangement.spacedBy(10.dp)
        ) {
            val sampleDecisions = listOf(
                "Delegated Q4 Competitive Analysis to Research Department (Dr. Aris Vance)",
                "Directed Marketing to formulate 3 organic TikTok hooks for Glassmorphism 2.0 release",
                "Reconciled conflicting task priorities in Operations to eliminate redundant research pipelines",
                "Approved Technology's internal unit test suite expansion to 41 automated assertions",
                "Scheduled Sunday Executive Board meeting for Africa/Algiers timezone consolidation",
                "Allocated free-tier Groq and OpenRouter quotas to optimize response latency"
            )

            items(sampleDecisions) { decision ->
                GlassCard(
                    modifier = Modifier.fillMaxWidth(),
                    borderColor = NeonCyan.copy(alpha = 0.2f)
                ) {
                    Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Text(
                                text = "AUTONOMOUS DECISION",
                                color = NeonEmerald,
                                fontSize = 10.sp,
                                fontWeight = FontWeight.Bold
                            )
                            Text(
                                text = "EXECUTED",
                                color = TextTertiary,
                                fontSize = 10.sp
                            )
                        }
                        Text(
                            text = decision,
                            color = TextPrimary,
                            fontSize = 13.sp,
                            lineHeight = 18.sp
                        )
                    }
                }
            }
        }
    }
}
