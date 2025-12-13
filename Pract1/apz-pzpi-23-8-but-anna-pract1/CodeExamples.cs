// Структура коду.
// Приклад поганого коду.
using System.Text;
using Xunit;

namespace CityGuide
{
    public class WeatherForecast
    {
    }
    public class MapHelper
    {
    }
}

// Приклад хорошого коду.
namespace CityGuide.Models
{
    public class WeatherForecast
    {
        public string City { get; set; }
        public string Summary { get; set; }
        public int TemperatureC { get; set; }
    }
}

//Форматування коду.
//Приклад поганого коду.
class Calculator
{
    public int Add(int a, int b)
    {
        int result = a + b;
        Console.WriteLine("Result:" + result);
        return result;
    }
}

//Приклад хорошого коду.
public class Calculator
{
    public int Add(int a, int b)
    {
        int result = a + b;
        Console.WriteLine($"Result: {result}");
        return result;
    }
}

//Іменування.
//Приклад поганого коду.
public int cs(int[] n)
{
    int t = 0;
    foreach (int x in n)
    {
        t += x;
    }
    return t;
}

//Приклад хорошого коду.
public int CalculateSum(int[] numbers)
{
    int totalSum = 0;
    foreach (int number in numbers)
    {
        totalSum += number;
    }
    return totalSum;
}

bool IsPrime(int x) //перевірка числа
{
    if (x <= 1) return false;

    for (int i = 2; i * i <= x; i++)
    {
        if (x % i == 0)
            return false;
    }

    return true;
}

// Повертає true, якщо число просте, а інакше false.
bool IsPrime(int n)
{
    if (n <= 1) return false;

    for (int i = 2; i * i <= n; i++)
    {
        if (n % i == 0)
            return false;
    }

    return true;
}

// Документування коду.
namespace TemperatureConversion
{
    /// <summary>
    /// The <c>Temperature</c> class provides functions for converting 
    /// temperature values between different scales.
    /// </summary>
    public class Temperature
    {
        /// <summary>
        /// Converts degrees Celsius to degrees Fahrenheit.
        /// </summary>
        /// <param name="degreesCelsius">Temperature in degrees Celsius.</param>
        /// <returns>Returns the temperature in degrees Fahrenheit.</returns>
        public static int CelsiusToFahrenheit(int degreesCelsius)
        {
            return (int)((9.0 / 5.0) * degreesCelsius + 32);
        }

        /// <summary>
        /// Converts degrees Fahrenheit to degrees Celsius.
        /// </summary>
        /// <param name="degreesFahrenheit">Temperature in degrees Fahrenheit.</param>
        /// <returns>Returns the temperature in degrees Celsius.</returns>
        public static int FahrenheitToCelsius(int degreesFahrenheit)
        {
            return (int)((5.0 / 9.0) * (degreesFahrenheit - 32));
        }
    }
}

//Кодування на основі тестування.
public class TranslatorTest
    {
        [Fact]
        public void TestOneTranslation()
        {
            var t = new Translator();
            t.Add("hello", "bonjour");
            Assert.Equal("bonjour", t.Get("hello"));
        }
    }

    public class Translator
    {
        private Dictionary<string, string> _dict = new();

        public void Add(string word, string translation)
        {
            _dict[word] = translation;
        }

        public string Get(string word)
        {
            return _dict[word];
        }
    }

// Приклади оформлення коду.
//Приклад поганого коду.
class program
    {
        static void Main()
        {
            List<string> n = new List<string> { "Taras", "Olha" };
            var messageBuilder = new StringBuilder();
            string msg = "";
            for (int i = 0; i < n.Count; i++)
            {
                messageBuilder.AppendLine($"{i + 1}) {n[i]}");
            }
            Console.WriteLine("Список імен:\n" + msg);
        }
    }

//Приклад хорошого коду.
public class NameConcatenator
    {
        public static void Main()
        {
            var names = new List<string> { "Taras", "Olha" };
            var messageBuilder = new StringBuilder();

            for (int i = 0; i < names.Count; i++)
            {
                messageBuilder.AppendLine($"{i + 1}) {names[i]}");
            }

            Console.WriteLine("Список імен:\n" + messageBuilder);
        }
    }