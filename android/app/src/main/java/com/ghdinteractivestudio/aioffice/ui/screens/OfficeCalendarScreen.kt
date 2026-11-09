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
fun OfficeCalendarScreen(viewModel: OfficeViewModel) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        Text(
            text = "OFFICE CALENDAR & CADENCE",
            color = NeonCyan,
            fontSize = 20.sp,
            fontWeight = FontWeight.Bold
        )
        Text(
            text = "Automated executive schedule calibrated to Africa/Algiers timezone.",
            color = TextSecondary,
            fontSize = 12.sp
        )

        Spacer(modifier = Modifier.height(16.dp))

        val events = listOf(
            Triple("Daily Executive Briefing", "Every Day at 08:00 (Africa/Algiers)", "AI CEO consolidates 24h progress and prepares briefing for Human Owner."),
            Triple("Sunday Executive Board Meeting", "Every Sunday at 10:00 (Africa/Algiers)", "Director reports consolidated, weekly performance reviewed, roadmap updated."),
            Triple("Weekly Knowledge Library Hour", "Every Wednesday at 15:00 (Africa/Algiers)", "Research department grounds and organizes newly acquired corporate knowledge.")
        )

        LazyColumn(verticalArrangement = Arrangement.spacedBy(12.dp)) {
            items(events.size) { index ->
                val (name, time, desc) = events[index]
                GlassCard(modifier = Modifier.fillMaxWidth()) {
                    Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Text(name, color = NeonEmerald, fontSize = 14.sp, fontWeight = FontWeight.Bold)
                            Text("SCHEDULED", color = TextTertiary, fontSize = 10.sp)
                        }
                        Text(time, color = NeonAmber, fontSize = 12.sp, fontWeight = FontWeight.SemiBold)
                        Text(desc, color = TextSecondary, fontSize = 12.sp, lineHeight = 16.sp)
                    }
                }
            }
        }
    }
}
