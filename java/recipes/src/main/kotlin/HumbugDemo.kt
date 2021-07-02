import dev.bugout.humbug.*

import kotlin.Exception

val consent = HumbugConsent(true)

const val TOKEN = "95cfa467-94ae-4891-951b-7874d6a13e2c"
val reporter = Reporter("kotlin-reporter", consent, "400", "400", TOKEN)

fun main() {
    val tags = arrayOf("demo", "kotlin", "kotlin_version:${KotlinVersion.CURRENT}")

    reporter.systemReport(*tags)
    try {
        throw KotlinNullPointerException("message")
    }
    catch (e: Exception){
        reporter.errorReport(e, *tags)
    }

    reporter.customReport("Custom", "Hello from kotlin", *tags)
}

