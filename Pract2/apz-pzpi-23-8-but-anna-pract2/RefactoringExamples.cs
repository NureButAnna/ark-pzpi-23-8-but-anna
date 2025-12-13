
// Метод «Decompose Conditional» (Розподіл умовного оператора).
// До рефакторингу.
using System;

public class BonusCalculator
{
    public double CalculateBonus(double salary, int yearsOfExperience, double performanceRating)
    {
        double bonus;

        if (yearsOfExperience > 5 && performanceRating >= 4.5)
        {
            bonus = salary * 0.2;
        }
        else
        {
            if (performanceRating >= 4.0)
            {
                bonus = salary * 0.1;
            }
            else
            {
                bonus = 0;
            }
        }

        return bonus;
    }
}

// Після рефакторингу(Decompose Conditional).
public class BonusCalculator
{
    public double CalculateBonus(double salary, int yearsOfExperience, double performanceRating)
    {
        if (IsTopPerformer(yearsOfExperience, performanceRating))
            return HighBonus(salary);
        else if (IsGoodPerformer(performanceRating))
            return MediumBonus(salary);
        else
            return NoBonus();
    }

    private bool IsTopPerformer(int yearsOfExperience, double performanceRating)
    {
        return yearsOfExperience > 5 && performanceRating >= 4.5;
    }

    private bool IsGoodPerformer(double performanceRating)
    {
        return performanceRating >= 4.0;
    }

    private double HighBonus(double salary)
    {
        return salary * 0.2;
    }

    private double MediumBonus(double salary)
    {
        return salary * 0.1;
    }

    private double NoBonus()
    {
        return 0;
    }
}

// Метод «Hide Method».
// До рефакторингу.
public class Order
{
    public double CalculateTotal(double amount)
    {
        double discount = CalculateDiscount(amount);
        return amount - discount;
    }

    public double CalculateDiscount(double amount)
    {
        if (amount > 1000)
            return amount * 0.1;
        else
            return 0;
    }
}

// Після рефакторингу.
public class Order
{
    public double CalculateTotal(double amount)
    {
        double discount = CalculateDiscount(amount);
        return amount - discount;
    }

    private double CalculateDiscount(double amount)
    {
        if (amount > 1000)
            return amount * 0.1;
        else
            return 0;
    }
}


// Метод «Replace Error Code with Exception».
// До рефакторингу.
public class BankAccount
{
    private double _balance;

    public BankAccount(double initialBalance)
    {
        _balance = initialBalance;
    }

    // Повертає 0 – успіх, -1 – недостатньо коштів, -2 – неправильна сума.
    public int Withdraw(double amount)
    {
        if (amount <= 0)
        {
            return -2;
        }
        if (amount > _balance)
        {
            return -1;
        }

        _balance -= amount;
        return 0;
    }

    public double GetBalance()
    {
        return _balance;
    }
}
 
// Після рефакторингу.
public class BankAccount
{
    private double _balance;

    public BankAccount(double initialBalance)
    {
        _balance = initialBalance;
    }

    public void Withdraw(double amount)
    {
        if (amount <= 0)
        {
            throw new ArgumentException("Сума повинна бути більшою за нуль.");
        }
        if (amount > _balance)
        {
            throw new InvalidOperationException("Недостатньо коштів на рахунку.");
        }

        _balance -= amount;
    }

    public double GetBalance()
    {
        return _balance;
    }
}


