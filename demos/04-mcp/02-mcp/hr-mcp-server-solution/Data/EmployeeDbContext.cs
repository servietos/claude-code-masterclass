using HRMCPServer;
using Microsoft.EntityFrameworkCore;

namespace HRMCPServer.Data;

public class EmployeeDbContext : DbContext
{
    public EmployeeDbContext(DbContextOptions<EmployeeDbContext> options)
        : base(options)
    {
    }

    public DbSet<Employee> Employees => Set<Employee>();
    public DbSet<ShiftAssignment> ShiftAssignments => Set<ShiftAssignment>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        var employeeEntity = modelBuilder.Entity<Employee>();

        employeeEntity.ToTable("Candidates");

        employeeEntity.HasKey(c => c.Id);

        employeeEntity.Property(c => c.FirstName)
            .IsRequired()
            .HasMaxLength(100);

        employeeEntity.Property(c => c.LastName)
            .IsRequired()
            .HasMaxLength(100);

        employeeEntity.Property(c => c.Email)
            .IsRequired()
            .HasMaxLength(256);

        employeeEntity.HasIndex(c => c.Email)
            .IsUnique();

        employeeEntity.Property(c => c.CurrentRole)
            .HasMaxLength(200);

        employeeEntity.Property(c => c.SpokenLanguagesData)
            .IsRequired()
            .HasColumnType("TEXT");

        employeeEntity.Property(c => c.SkillsData)
            .IsRequired()
            .HasColumnType("TEXT");

        var shiftEntity = modelBuilder.Entity<ShiftAssignment>();

        shiftEntity.ToTable("ShiftAssignments");
        shiftEntity.HasKey(s => s.Id);

        shiftEntity.Property(s => s.Position)
            .IsRequired()
            .HasMaxLength(100);

        shiftEntity.Property(s => s.EmployeeName)
            .IsRequired()
            .HasMaxLength(200);

        shiftEntity.Ignore(s => s.ShiftEndHour);

        shiftEntity.HasOne<Employee>()
            .WithMany()
            .HasForeignKey(s => s.EmployeeId)
            .OnDelete(DeleteBehavior.Cascade);
    }
}
