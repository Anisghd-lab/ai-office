package com.ghdinteractivestudio.aioffice.ui.components

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxScope
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import com.ghdinteractivestudio.aioffice.ui.theme.GlassBorder
import com.ghdinteractivestudio.aioffice.ui.theme.GlassFill
import com.ghdinteractivestudio.aioffice.ui.theme.GlassFillSubtle

@Composable
fun GlassCard(
    modifier: Modifier = Modifier,
    cornerRadius: Dp = 20.dp,
    borderColor: Color = GlassBorder,
    borderWidth: Dp = 1.dp,
    content: @Composable BoxScope.() -> Unit
) {
    val shape = RoundedCornerShape(cornerRadius)
    val gradientBrush = Brush.verticalGradient(
        colors = listOf(
            GlassFill,
            GlassFillSubtle
        )
    )

    Box(
        modifier = modifier
            .clip(shape)
            .background(gradientBrush)
            .border(
                border = BorderStroke(borderWidth, borderColor),
                shape = shape
            )
            .padding(16.dp),
        content = content
    )
}
