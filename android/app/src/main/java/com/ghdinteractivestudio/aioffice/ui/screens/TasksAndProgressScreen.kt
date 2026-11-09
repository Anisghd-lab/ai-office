package com.ghdinteractivestudio.aioffice.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.ghdinteractivestudio.aioffice.ui.components.GlassCard
import com.ghdinteractivestudio.aioffice.ui.theme.*
import com.ghdinteractivestudio.aioffice.viewmodel.OfficeViewModel

@Composable
fun TasksAndProgressScreen(viewModel: OfficeViewModel) {
    val tasks by viewModel.tasks.collectAsState()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        Text(
            text = "TASKS & PROGRESS",
            color = NeonCyan,
            fontSize = 20.sp,
            fontWeight = FontWeight.Bold
        )
        Text(
            text = "Active, completed, and assigned cross-departmental initiatives.",
            color = TextSecondary,
            fontSize = 12.sp
        )

        Spacer(modifier = Modifier.height(16.dp))

        LazyColumn(verticalArrangement = Arrangement.spacedBy(10.dp)) {
            items(tasks) { task ->
                GlassCard(modifier = Modifier.fillMaxWidth()) {
                    Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Text(
                                text = task.title,
                                color = TextPrimary,
                                fontSize = 14.sp,
                                fontWeight = FontWeight.Bold,
                                modifier = Modifier.weight(1f)
                            )
                            Text(
                                text = task.status,
                                color = when (task.status) {
                                    "COMPLETED" -> NeonEmerald
                                    "IN_PROGRESS" -> NeonCyan
                                    "ASSIGNED" -> NeonAmber
                                    else -> TextSecondary
                                },
                                fontSize = 11.sp,
                                fontWeight = FontWeight.Bold
                            )
                        }

                        if (!task.description.isNullOrBlank()) {
                            Text(
                                text = task.description,
                                color = TextSecondary,
                                fontSize = 12.sp
                            )
                        }

                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Text(
                                text = "Dept: ${task.departmentId} • Priority: ${task.priority}",
                                color = TextTertiary,
                                fontSize = 11.sp
                            )
                            Text(
                                text = "${task.progressPct}%",
                                color = NeonCyan,
                                fontSize = 11.sp,
                                fontWeight = FontWeight.Bold
                            )
                        }

                        LinearProgressIndicator(
                            progress = { (task.progressPct / 100f).coerceIn(0f, 1f) },
                            modifier = Modifier.fillMaxWidth(),
                            color = NeonCyan,
                            trackColor = GlassFill,
                        )
                    }
                }
            }
        }
    }
}
