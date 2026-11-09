package com.ghdinteractivestudio.aioffice.ui.screens

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.ghdinteractivestudio.aioffice.ui.components.GlassCard
import com.ghdinteractivestudio.aioffice.ui.theme.*
import com.ghdinteractivestudio.aioffice.viewmodel.OfficeViewModel

@Composable
fun PendingUserApprovalsScreen(viewModel: OfficeViewModel) {
    val approvals by viewModel.approvals.collectAsState()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        Text(
            text = "PENDING USER APPROVALS",
            color = NeonAmber,
            fontSize = 20.sp,
            fontWeight = FontWeight.Bold
        )
        Text(
            text = "Mandatory Human Owner Authorization Gateway. External side-effects cannot execute without your sign-off.",
            color = TextSecondary,
            fontSize = 12.sp
        )

        Spacer(modifier = Modifier.height(16.dp))

        if (approvals.isEmpty()) {
            GlassCard(
                modifier = Modifier.fillMaxWidth(),
                borderColor = NeonEmerald.copy(alpha = 0.3f)
            ) {
                Column(
                    modifier = Modifier.padding(12.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Text(
                        text = "All Clear — Zero Pending Requests",
                        color = NeonEmerald,
                        fontSize = 15.sp,
                        fontWeight = FontWeight.Bold
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = "The AI CEO and departments are currently operating autonomously within internal boundaries.",
                        color = TextSecondary,
                        fontSize = 12.sp
                    )
                }
            }
        } else {
            LazyColumn(verticalArrangement = Arrangement.spacedBy(14.dp)) {
                items(approvals) { item ->
                    GlassCard(
                        modifier = Modifier.fillMaxWidth(),
                        borderColor = NeonAmber.copy(alpha = 0.6f)
                    ) {
                        Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceBetween
                            ) {
                                Text(
                                    text = "${item.actionType} → ${item.destination}",
                                    color = NeonCyan,
                                    fontSize = 14.sp,
                                    fontWeight = FontWeight.Bold
                                )
                                Text(
                                    text = "RISK: ${item.riskLevel}",
                                    color = NeonAmber,
                                    fontSize = 11.sp,
                                    fontWeight = FontWeight.Bold
                                )
                            }

                            Text(
                                text = "Proposing Agent: ${item.agentId} (${item.departmentId})",
                                color = TextSecondary,
                                fontSize = 11.sp
                            )

                            GlassCard(
                                modifier = Modifier.fillMaxWidth(),
                                borderColor = GlassBorder
                            ) {
                                Column {
                                    Text(
                                        text = "EXACT ACTION PAYLOAD:",
                                        color = TextTertiary,
                                        fontSize = 10.sp,
                                        fontWeight = FontWeight.Bold
                                    )
                                    Spacer(modifier = Modifier.height(4.dp))
                                    Text(
                                        text = item.payload,
                                        color = TextPrimary,
                                        fontSize = 12.sp,
                                        lineHeight = 16.sp
                                    )
                                }
                            }

                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.SpaceBetween
                            ) {
                                Text(
                                    text = "Cost: $0.00 (Zero-Cost)",
                                    color = NeonEmerald,
                                    fontSize = 11.sp
                                )
                                Text(
                                    text = "Hash: ${item.payloadHash.take(12)}...",
                                    color = TextTertiary,
                                    fontSize = 11.sp
                                )
                            }

                            Row(
                                modifier = Modifier.fillMaxWidth(),
                                horizontalArrangement = Arrangement.spacedBy(12.dp)
                            ) {
                                Button(
                                    onClick = { viewModel.approvePendingAction(item.id) },
                                    modifier = Modifier.weight(1f),
                                    colors = ButtonDefaults.buttonColors(containerColor = NeonEmerald)
                                ) {
                                    Text("APPROVE", color = DeepBlackBg, fontWeight = FontWeight.Bold)
                                }

                                Button(
                                    onClick = { viewModel.rejectPendingAction(item.id, "Owner rejected") },
                                    modifier = Modifier.weight(1f),
                                    colors = ButtonDefaults.buttonColors(containerColor = NeonRose)
                                ) {
                                    Text("REJECT", color = TextPrimary, fontWeight = FontWeight.Bold)
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
