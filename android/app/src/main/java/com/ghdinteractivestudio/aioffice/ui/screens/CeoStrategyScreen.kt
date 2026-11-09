package com.ghdinteractivestudio.aioffice.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.ghdinteractivestudio.aioffice.ui.components.GlassCard
import com.ghdinteractivestudio.aioffice.ui.theme.*
import com.ghdinteractivestudio.aioffice.viewmodel.OfficeViewModel

@Composable
fun CeoStrategyScreen(viewModel: OfficeViewModel) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        Text(
            text = "AI CEO CORPORATE STRATEGY",
            color = NeonCyan,
            fontSize = 20.sp,
            fontWeight = FontWeight.Bold
        )

        GlassCard(
            modifier = Modifier.fillMaxWidth(),
            borderColor = NeonAmber.copy(alpha = 0.4f)
        ) {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text(
                    text = "EXECUTIVE VISION",
                    color = NeonAmber,
                    fontSize = 12.sp,
                    fontWeight = FontWeight.Bold
                )
                Text(
                    text = "Operate an elite, fully autonomous multi-department AI enterprise under zero commercial infrastructure cost, with strict human user authorization for external side effects.",
                    color = TextPrimary,
                    fontSize = 14.sp,
                    lineHeight = 20.sp
                )
            }
        }

        // Strategic Pillars
        val pillars = listOf(
            Pair("Pillar I: Autonomous Operations", "Internal task generation, debate, planning, code generation, and factual validation occur continuously without stalling."),
            Pair("Pillar II: Mandatory User Gateway", "The human owner retains exclusive sign-off on publishing, messaging, spending, and credential changes."),
            Pair("Pillar III: Zero-Cost Infrastructure", "Strictly enforce zero expenditures by utilizing free provider quotas, local Ollama endpoints, and open platforms."),
            Pair("Pillar IV: Native Android Command", "Full low-latency control via Kotlin 2.0 Jetpack Compose with Glassmorphism 2.0 aesthetics on 127.0.0.1.")
        )

        pillars.forEach { (title, desc) ->
            GlassCard(modifier = Modifier.fillMaxWidth()) {
                Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                    Text(title, color = NeonCyan, fontSize = 14.sp, fontWeight = FontWeight.Bold)
                    Text(desc, color = TextSecondary, fontSize = 12.sp, lineHeight = 18.sp)
                }
            }
        }
    }
}
