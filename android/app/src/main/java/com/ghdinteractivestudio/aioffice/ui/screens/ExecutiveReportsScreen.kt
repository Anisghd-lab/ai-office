package com.ghdinteractivestudio.aioffice.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
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
fun ExecutiveReportsScreen(viewModel: OfficeViewModel) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        Text(
            text = "EXECUTIVE REPORTS",
            color = NeonCyan,
            fontSize = 20.sp,
            fontWeight = FontWeight.Bold
        )
        Text(
            text = "Daily briefings and consolidated weekly executive minutes generated for the Owner.",
            color = TextSecondary,
            fontSize = 12.sp
        )

        Spacer(modifier = Modifier.height(16.dp))

        LazyColumn(verticalArrangement = Arrangement.spacedBy(12.dp)) {
            val sampleReports = listOf(
                Pair("Daily Executive Briefing (08:00 Algiers)", "Status: OPERATIONAL • 8 Departments Active • Cost: $0.00 • Factual Integrity: 100%"),
                Pair("Sunday Executive Board Meeting Minutes", "Reviewed weekly throughput • Zero quota violations • Cross-departmental KPIs achieved"),
                Pair("Research & Intelligence Market Scan", "Identified 4 open-weight model architectures for low-latency local inference"),
                Pair("Finance & Guardrail Zero-Cost Audit", "Verified $0.00 total spend • Rolling RPM within provider boundaries")
            )

            items(sampleReports.size) { index ->
                val (title, summary) = sampleReports[index]
                GlassCard(modifier = Modifier.fillMaxWidth()) {
                    Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                        Text(
                            text = title,
                            color = TextPrimary,
                            fontSize = 14.sp,
                            fontWeight = FontWeight.Bold
                        )
                        Text(
                            text = summary,
                            color = TextSecondary,
                            fontSize = 12.sp,
                            lineHeight = 18.sp
                        )
                    }
                }
            }
        }
    }
}
